import os
import gc
import sys

from chooser import *
from eval import eval
import md5

from port import viewport

from random import shuffle

from multiprocessing import Process,JoinableQueue,Value,Manager,RLock

import copy
from map import *

import time

bigNumber = 5000000000
numProcs = 16
multiProc=True
maxDepth = 30
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
        self.prevPos = None
        self.posList = []

    def copy(self, old):
        self.posList = list(old.posList)
        self.viewList = list(old.viewList)
        self.lastMoveDir = old.lastMoveDir
        self.moveList = list(old.moveList)
        self.prevPos = old.prevPos
        self.posList = old.posList

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
    state.posList = [map.robot_pos]
    state.prevPos = map.robot_pos

    jobs = []

    longestSolution = Value('d', 20)
    highestScore = Value('d', 0)

    queue = JoinableQueue()

    manager = Manager()

    d = manager.dict()
    d.clear()

    l = RLock()

    if multiProc:
        queue.put((state, map, 1))

        for i in range(numProcs):
           p = Process(target = multiMain, args=(startMap, l, d, queue,highestScore))
           p.start()

        queue.join()
    else:
        a(l, highestScore, d, None, state, map, 1)

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

def multiMain(sm, l, d, q, hs):
    startMap = sm

    while(True):
        (state, map, depth) = q.get()

        a(l, hs, d, q,state,map,depth)

        q.task_done()

def getValidMoves(map):
    valid = []
    #moves = [MOVE_UP,MOVE_DOWN,MOVE_RIGHT,MOVE_LEFT,MOVE_WAIT]
    moves = [MOVE_UP,MOVE_DOWN,MOVE_RIGHT,MOVE_LEFT]
    for dir in moves:
        if map.valid_move(dir):
            valid.append(dir)

    return valid

def removeMove(dir, validMoves):
    if dir in validMoves:
        idx = validMoves.index(dir)
        validMoves.pop(idx)

def doMove(l, hs,d, q,state,map,depth, move):
    newMap = Map()
    newMap.copy(map)

    newState = State()
    newState.copy(state)

    tryMove(l, hs,d,q,newState,newMap,move,depth)

def a(l, hs,d, q,state,map,depth):
    validMoves = getValidMoves(map)

    chooserState = {}

    move = chooseDir(l, hs,d, q,state,map,depth, validMoves, chooserState)
    while move != None:
        removeMove(move, validMoves)

        #print os.getpid(), "Evaling..."
        doMove(l, hs,d, q,state,map,depth, move)
        #print os.getpid(), "Done"
        move = chooseDir(l, hs,d, q,state,map,depth, validMoves, chooserState)

def tryMove(l, hs, d,q,state,map,move,depth):
    state.prevPos = map.robot_pos
    state.posList.append(map.robot_pos)

    map.move(move)

    if knownMap(l, d, state, map):
        return 

    if map.robot_pos == state.prevPos:
        return

    if map.died:
        return 

    evalMove(l, hs, d, state, map, move, state.prevPos)

    recurse(l, hs, d, q,state,map,move,depth)

def recurse(l, hs, d, q,state,map,move,depth):
    if len(state.moveList) != depth:
        print "Moves", state.moveList, len(state.moveList), depth
        
    if (depth+1) >=(map.width*map.height):
        #print "Bailing past maxDepth", depth+1, maxDepth
        return 

    if map.died:
        #print "Bailing, died"
        return 

    if map.done:
        #print "Success!"
        return

    if queueOk(q):
        q.put((state,map,depth+1))
    else:
        a(l, hs,d,q,state,map,depth+1)

def queueOk(q):
    if sys.platform == 'darwin':
        return q != None and not q.full()

    return q != None and q.qsize() < 1000

def evalMove(l, hs,d, state,map,move, prevPos):
    state.moveList.append(move)

    score = calcScore(state, map)

    #if map.done:
        #solved(score, state, map)

    evalScore(l, hs,d, score, state, map)

def solved(score, state, map):
    numMoves = len(state.moveList)

    print "Solved in", numMoves
    print "Solution: ", "".join(state.moveList)
    print "Score: ", score

    #print "Success in " + str(l) +  " moves: " +\
        #"".join(state.moveList) + " vs " + str(longestSolution.value),\
        #"Score: ", score
    print

def evalScore(l, hs,d, score, state, map):
    if score > hs.value:
        hs.value = score
        numMoves = len(state.moveList)

        path = "".join(state.moveList)

        if not map.done:
            path += MOVE_ABORT

        print ""
        print "New high score", score
        print "Moves taken", numMoves
        print "Path: ", path
        print "Map: "
        print map

        #map = Map()
        #print startMap
        #map.copy(startMap)

        #eval(path, map)

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

            #for (y,row) in enumerate(map.map):
                #for (x, cell) in enumerate(row):
                    #if oldMap.map[y][x] != cell:
                        #print "WTF, They aren't the same"
                        #print map
                        #print oldMap

            #print "----------------------------"
            #l.release()
            return True

        stateCopy = State()
        stateCopy.copy(state)
        d[hashVal] = (stateCopy, map)
        #l.release()
        return False
    except Exception as e:
        if nesting < 3:
            l.acquire()
            res = _knownMap(l, d, state, map, nesting+1)
            l.release()
            return res
        else:
            print "Failed after ", nesting, "nested calls"


def getHash(map):
    m = md5.new()

    for row in map.map:
        m.update(str(row))
    m.update(str(map.lams))
    m.update(str(map.robot_pos))

    return m.hexdigest()

