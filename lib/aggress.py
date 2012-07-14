import os
import gc
import sys

from eval import eval
import md5

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

    def copy(self, old):
        self.posList = list(old.posList)
        self.viewList = list(old.viewList)
        self.lastMoveDir = old.lastMoveDir
        self.moveList = list(old.moveList)

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
    moves = [MOVE_UP,MOVE_DOWN,MOVE_RIGHT,MOVE_LEFT,MOVE_WAIT]
    #moves = [MOVE_UP,MOVE_DOWN,MOVE_RIGHT,MOVE_LEFT]
    for dir in moves:
        if map.valid_move(dir):
            valid.append(dir)

    return valid

def a(l, hs,d, q,state,map,depth):
    if knownMap(l, d, state, map):
        return 

    validMoves = getValidMoves(map)

    shuffle(validMoves)

    #print map
    #print validMoves

    for move in validMoves:
        newMap = Map()
        newMap.copy(map)

        tryMove(l, hs,d,q,state,newMap,move,depth)

def getHash(map):
    m = md5.new()

    for row in map.map:
        m.update(str(row))
    m.update(str(map.lams))
    m.update(str(map.robot_pos))

    return m.hexdigest()

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
            l.acquire()
            res = _knownMap(l, d, state, map, nesting+1)
            l.release()
            return res
        else:
            print "Failed after ", nesting, "nested calls"


def tryMove(l, hs, d,q,oldState,map,move,depth):
    prevPos = map.robot_pos

    map.move(move)

    if map.died:
        return 

    # Now copy state, since we're going with this move
    state = State()
    state.copy(oldState)

    evalMove(l, hs, d, state, map, move, prevPos)

    recurse(l, hs, d, q,state,map,move,depth)

def recurse(l, hs, d, q,state,map,move,depth):
    if (depth+1) > maxDepth:
        #print "Bailing past maxDepth", depth+1
        return 

    if map.died:
        #print "Bailing, died"
        return 

    if map.done:
        #print "Success!"
        return

    if q != None and not q.full():
        q.put((state,map,depth+1))
    else:
        a(l, hs,d,q,state,map,depth+1)

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
