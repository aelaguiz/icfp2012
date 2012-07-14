import os
import gc
import sys

from eval import eval
import md5

from priority import *

from port import viewport

from random import shuffle

from multiprocessing import Process,JoinableQueue,Value,Manager,RLock

import copy
from map import *

import lib

import time

bigNumber = 5000000000
numProcs = 16
multiProc=True
maxDepth = 80
startMap = None

class State:
    def __init__(self):
        # List of positions we've been in since the last time the map
        # changed
        self.posList = []
        # Viewports at each move
        self.viewList = []
        # The actual direction of our last move, excluding waits
        self.lastMoveDir = None
        self.moveList = []
        self.hs = None
        self.score = 0

    def copy(self, old):
        self.posList = list(old.posList)
        self.viewList = list(old.viewList)
        self.lastMoveDir = old.lastMoveDir
        self.moveList = list(old.moveList)
        self.score = old.score

    def __repr__(self):
        res = "".join(self.moveList) + "\n"

        for i,move in enumerate(self.moveList):
            res += "{0} {1} {2}\n".format(i,move,self.viewList[i])
        return res

    def getTrainingData(self):
        classes = []
        samples = []

        #samples += [{ i+1: v for (i,v) in enumerate(row[1])}]
        for i,move in enumerate(self.moveList):
            view = self.viewList[i]

            classes.append(move)
            samples += [{ j+1: v for (j,v) in enumerate(self.viewList[i])}]

        return (classes, samples)

# Contest1 = DLLDDRRLLL

def aggress(map):
    global startMap
    startMap = map

    #print "Regressing..."
    state = State()

    jobs = []

    longestSolution = Value('d', 20)
    hs = Value('d', 0)


    manager = Manager()

    d = manager.dict()
    d.clear()

    queue = manager.list()

    l = RLock()
    ql = RLock()

    recurseValidMoves(l, hs, d, queue, ql, state, map, 0)

    if multiProc:
        procs = []

        for i in range(numProcs):
           p = Process(target = multiMain, args=(startMap, l, d, queue,ql, hs))
           p.start()
           procs.append(p)

        #for p in procs:
            #p.join()

    else:
        multiMain(startMap, l, d, queue, ql, hs)

def multiMain(sm, l, d, q, ql,  hs):
    startMap = sm

    while(True):
        #(state, map, depth) = q.get()

        #print os.getpid(), "Trying to dequeue...", len(q)
        res = dequeue(ql, q)
        while None == res:
            #print os.getpid(), "Waiting a second..."
            time.sleep(1)
            #print os.getpid(), "Trying again to dequeue...", len(q)
            res = dequeue(ql, q)
            #print os.getpid(), "Back from dequeue"

        (state, map, move, depth) = res

        #print os.getpid(), "Evaluating"
        a(l, hs, d, q, ql, state,map,move, depth)
        #print os.getpid(), "Done"

        #q.task_done()

def getValidMoves(map):
    valid = []
    moves = [MOVE_UP,MOVE_DOWN,MOVE_RIGHT,MOVE_LEFT,MOVE_WAIT]
    #moves = [MOVE_UP,MOVE_DOWN,MOVE_RIGHT,MOVE_LEFT]
    for dir in moves:
        if map.valid_move(dir):
            valid.append(dir)

    return valid

def recurseValidMoves(l, hs, d, q, ql, state, map, depth):
    validMoves = getValidMoves(map)

    shuffle(validMoves)

    for move in validMoves:
        #tryMove(l, hs,d,q, ql, state,newMap,move,depth)
        recurse(l, hs, d, q, ql, state,map,move,depth)


def a(l, hs,d, q, ql, state,map,move, depth):
    if tryMove(l, hs,d,q, ql, state,map,move,depth):
        recurseValidMoves(l, hs, d, q, ql, state, map, depth)

def getHash(map):
    m = md5.new()

    for row in map.map:
        m.update(str(row))
    m.update(str(map.lams))
    m.update(str(map.robot_pos))

    return m.hexdigest()


def tryMove(l, hs, d,q, ql, state,map,move,depth):
    prevPos = map.robot_pos

    map.move(move)

    if map.died:
        return False

    if knownMap(l, d, state, map):
        return False

    evalMove(l, hs, d, q, ql,  state, map, move, depth, prevPos)

    return True

def recurse(l, hs, d, q, ql, state,map,move,depth):
    if (depth+1) > maxDepth:
        #print "Bailing past maxDepth", depth+1
        return 

    if map.died:
        #print "Bailing, died"
        return 

    if map.done:
        #print "Success!"
        return

    newMap = Map()
    newMap.copy(map)

    newState = State()
    newState.copy(state)

    #if q != None and len(q) < 1000:
    if q != None:
        enqueue(q, (newState,newMap,move,depth+1), -state.score)
    #else:
        #a(l, hs,d,q, ql, state,map,depth+1)

def evalMove(l, hs,d, q, ql, state,map,move, depth,prevPos):
    state.moveList.append(move)

    state.score = calcScore(state, map)

    #if map.done:
        #solved(score, state, map)

    evalScore(l, hs,d, state, map)

    recurse(l, hs, d, q, ql, state,map,move,depth)

def evalScore(l, hs,d, state, map):
    if state.score > hs.value:
        hs.value = state.score
        numMoves = len(state.moveList)

        path = "".join(state.moveList)

        if not map.done:
            path += MOVE_ABORT

        print ""
        print "New high state.score", state.score
        print "Moves taken", numMoves
        print "Path: ", path

        map = Map()
        print startMap
        map.copy(startMap)

        eval(path, map)

        #checkHigher(l, hs, d, state, map)

def checkHigher(l, hs, d, oldState, oldMap):
    map = Map()
    map.copy(startMap)

    state = State()

    for move in oldState.moveList:
        map.move(move)
        state.moveList.append(move)

        hashVal = getHash(map)

        #l.acquire()
        if hashVal in d:
            (savedState, savedMap) = d[hashVal]

            newScore = calcScore(state,map)
            savedScore = calcScore(savedState, savedMap)

            if savedScore > newScore:
                print "Found higher scoring path"
                print newScore, oldState.moveList
                print savedScore, savedState.moveList
            elif savedScore < newScore:
                print "Found LOWER scoring path"
                print newScore, state.moveList
                print savedScore, savedState.moveList
        #l.release()

def knownMap(l, d, state, map):
    return _knownMap(l, d, state, map, 0)

def _knownMap(l, d, state, map, nesting):
    try:
        hashVal = getHash(map)

        #l.acquire()
        if hashVal in d:
            (oldState, oldMap) = d[hashVal]

            newScore = calcScore(state,map)
            oldScore = calcScore(oldState, oldMap)

            #print "----------------------------"
            #print state.moveList, newScore
            #print "gets us to the same spot as"
            #print oldState.moveList, oldScore

            if newScore > oldScore:
                #print "New score is higher, removing old entry"
                #print state.moveList, newScore
                #print oldState.moveList, oldScore
                del d[hashVal]
                #l.release()
                return False

            #print "Known map", map.lams, "Lams"
            #print map
            #print "Same as", oldMap.lams, "Lams"
            #print oldMap

            for (y,row) in enumerate(map.map):
                for (x, cell) in enumerate(row):
                    if oldMap.map[y][x] != cell:
                        print "WTF, They aren't the same"
                        print map
                        print oldMap

            #print "----------------------------"
            #l.release()
            return True

        stateCopy = State()
        stateCopy.copy(state)
        d[hashVal] = (stateCopy, map)
        #l.release()
        return False
    except:
        if nesting < 3:
            print "Trying again", nesting+1
            l.acquire()
            res = _knownMap(l, d, state, map, nesting+1)
            l.release()
            return res
        else:
            print "Failed after ", nesting, "nested calls"

def calcScore(state,map):
    score = 0
    score -= len(state.moveList)
    score += 25 * map.lams
    if map.done:
        score += 50 * map.lams
    else:
        # Assumption that we'll abort
        score += 25 * map.lams

    return score

