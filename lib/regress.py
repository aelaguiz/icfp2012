import os
import gc

from port import viewport

from random import shuffle

from multiprocessing import Process,JoinableQueue,Value

import copy
from map import *

import time

bigNumber = 5000000000
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
        self.maxDepth = 300

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

def regress(map):
    #print "Regressing..."
    state = State()

    jobs = []

    longestSolution = Value('d', 20)
    highestScore = Value('d', 0)

    queue = JoinableQueue()

    queue.put((state, map, MOVE_UP, 1))
    
    queue.put((state, map, MOVE_DOWN, 1))
    queue.put((state, map, MOVE_LEFT, 1))
    queue.put((state, map, MOVE_RIGHT, 1))
    queue.put((state, map, MOVE_WAIT, 1))

    for i in range(16):
        p = Process(target = l, args=(queue,longestSolution,highestScore))
        p.start()

    queue.join()

    #i = inspect()

    #while(True):
        #time.sleep(5)
        ##print i.active()

    #def getFinished():
         #return [ j for j in jobs if j.state == 'FAILURE' or j.state ==
                 #'SUCCESS' ]

    #finished = getFinished()
    #while len(finished) != len(jobs):
        #time.sleep(2)

        #finished = getFinished()

        ##print len(finished), "finished"


# Return the opposite direction
def opDir(dir):
    if dir == MOVE_UP:
        return MOVE_DOWN
    elif dir == MOVE_DOWN:
        return MOVE_UP
    elif dir == MOVE_RIGHT:
        return MOVE_LEFT
    elif dir == MOVE_LEFT:
        return MOVE_RIGHT

def updateLastMoveDir(state, move):
    if move == MOVE_WAIT:
        pass
    else:
        state.lastMoveDir = move

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

def l(q, longestSolution, highestScore):
    while(True):
        (state, map, move, depth) = q.get()

        r(q, state, map, move, depth, longestSolution,highestScore)

        q.task_done()
        #print "Task done"

def r(q,state, map, move, depth, longestSolution,highestScore):
    oldmap = map
    oldstate = state
    map = copy.deepcopy(oldmap)
    state = copy.deepcopy(oldstate)

    if map.move(move):
        # Well, we died - so probably not a great idea
        if map.died:
            #print "Died at depth", depth, "ended"
            return longestSolution.value

        # We tried to move NOT wait...but we didn't move. That means we're
        # trying to move into a wall 
        if map.robot_pos == oldmap.robot_pos and move != MOVE_WAIT:
            #print "Invalid move", depth, "ended"
            return longestSolution.value

        prevMove = None
        if len(state.moveList):
            prevMove = state.moveList[len(state.moveList)-1]

        state.viewList.append(viewport(map, map.robot_pos, oldmap.robot_pos,
            prevMove))

        state.moveList.append(move)
        #print "Took move: ", move, "recursion depth",depth, "total moves",len(state.moveList)
        #print "Move list: ",state.moveList
        #print oldmap
        #print map


        score = calcScore(state, map)

        if score > highestScore.value:
            scoreState = copy.deepcopy(state)

            if not map.done:
                scoreState.moveList.append(MOVE_ABORT)
                scoreState.viewList.append(viewport(map, map.robot_pos, map.robot_pos,
                    move))

            highestScore.value = score

            print "New high score",score, "".join(scoreState.moveList),\
                len(scoreState.moveList), "moves"
            print scoreState
            print scoreState.getTrainingData()

            l = len(scoreState.moveList)
            if l > longestSolution.value:
                longestSolution.value = l

        #if map.done:
            #l = len(state.moveList)
            #if l > longestSolution.value:
                #longestSolution.value = l
            #print "Success in " + str(l) +  " moves: " +\
                #"".join(state.moveList) + " vs " + str(longestSolution.value),\
                #"Score: ", score
            #print state
            #print state.getTrainingData()
            #return len(state.moveList)

        ## Caught in termination condition instead
        #if len(state.moveList) >= (longestSolution.value*1.25):
            ##print "Bailing not going more steps than our shortest solution of",\
           ##     longestSolution.value
            #return longestSolution.value

        ###
        ## Update the state following a move
        ###

        # Check to see if our current position is in the position list
        idx = -1
        try:
            idx = state.posList.index(map.robot_pos)
        except:
            pass

        # Loop prevention can terminate a branch if we hit a loop
        if move != MOVE_WAIT:
            # Prevent loops
            if not map.changed:
                # If a move takes us back to a cell we've visited and the map has not
                # changed since
                    # return False
                if idx != -1:
                    #print "Branch looped at depth", depth, "ended"
                    return longestSolution.value

        # If the map changed, clear the position list
        if map.changed:
            state.posList = []

        # Otherwise add our position to it (unless it's there)
        if idx == -1:
            state.posList.append(map.robot_pos)

        # Update the direction of our last move, taking into consideration waits
        updateLastMoveDir(state, move)

        ###
        ## Recursively continue regression
        ###

        moves = []
        
        for dir in [MOVE_UP,MOVE_DOWN,MOVE_RIGHT,MOVE_LEFT]:
            # If we're trying to go in a direction that is not the direction we
            # came from, try it
            if dir != opDir(state.lastMoveDir):
                moves.append(dir)
            # Or if we are turning around, but we changed the map - that is
            # okay
            elif map.changed:
                #print "Turning around after map changed"
                moves.append(dir)

        # If we already waited but the map changed, try again
        if move == MOVE_WAIT and map.changed:
            moves.append(MOVE_WAIT)
        # But if we waited and the map didn't change, don't wait again
        elif move == MOVE_WAIT:
            pass
        # else we didn't wait so, go ahead and try waiting
        else:
            moves.append(MOVE_WAIT)

                #lib.regress.r.delay(state, map, dir,depth+1)

        if len(moves) == 0:
            #print "Branch failed at depth", depth
            return longestSolution.value

        if (depth+1)>= state.maxDepth:
            #print "Branch died at depth", depth+1
            return longestSolution.value

        shuffle(moves)

        for move in moves:
            # Longest solution functions as an upper bound for further
            # exploration we don't go more than 25% deeper
            if longestSolution.value == 0 or (depth+1) < (longestSolution.value*2):
                #print "Eneuqing", state.moveList, move,depth+1

                if not q.full():
                #if q.qsize() < 1000:
                    q.put((state,map,move,depth+1))
                else:
                    #print "Queue is full, just recursing"
                    r(q, state, map, move, depth+1,\
                            longestSolution,highestScore)
            #else:
                #print "Not recursing because", depth+1, ">", longestSolution.value

    return longestSolution.value

    ## Movement rules
    # Try each direction that is NOT the direction we came from
    # Allowed to turn around IF we changed the map in some way the last move
        # Otherwise a turn around is not a valid operation
    # Only allowed to wait consecutively if the last wait produced a chnge in
        # the map
    # If a move takes us back to a cell we've visited and the map has not
    # changed since
        # return False
    # If we are out of valid operations, return False

    ## NOTE
    # We will need some sort of cycle detection because if the map looks like
    #
    #   R * .  
    # I can push the rock back and forth between a variety of states all of
    # which are changing the map but it is just a cycle


#### Old
## Can go back along the same path we took if the map has changed in some way
## since we last backtracked
    ## Backtracking means
