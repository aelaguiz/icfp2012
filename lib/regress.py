import os
import copy
from map import *

class State:
    def __init__(self):
        # List of positions we've been in since the last time the map
        # changed
        self.posList = []
        # The actual direction of our last move, excluding waits
        self.lastMoveDir = None
        self.moveList = []

def regress(map):
    state = State()

    if os.fork() == 0:
        return r(state, map, MOVE_UP, 1)

    if os.fork() == 0:
        return r(state, map, MOVE_DOWN, 1)

    if os.fork() == 0:
        return r(state, map, MOVE_LEFT, 1)

    if os.fork() == 0:
        return r(state, map, MOVE_RIGHT, 1)

    return r(state, map, MOVE_WAIT, 1)

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

def r(state, map, move, depth):
    oldmap = map
    oldstate = state
    map = copy.deepcopy(oldmap)
    state = copy.deepcopy(oldstate)

    if map.move(move):
        # Well, we died - so probably not a great idea
        if map.died:
            print "Died at depth", depth, "ended"
            return 

        # We tried to move NOT wait...but we didn't move. That means we're
        # trying to move into a wall 
        if map.robot_pos == oldmap.robot_pos and move != MOVE_WAIT:
            print "Invalid move", depth, "ended"
            return

        state.moveList.append(move)
        print "Took move: ", move, "recursion depth",depth, "total moves",len(state.moveList)
        print "Move list: ",state.moveList
        print oldmap
        print map

        if map.done:
            print "Success in", len(state.moveList), "moves:", state.moveList
            return 

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
                    print "Branch looped at depth", depth, "ended"
                    return 

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
        
        for dir in [MOVE_UP,MOVE_DOWN,MOVE_RIGHT,MOVE_LEFT]:
            # If we're trying to go in a direction that is not the direction we
            # came from, try it
            if dir != opDir(state.lastMoveDir):
                r(state, map, dir,depth+1)
            # Or if we are turning around, but we changed the map - that is
            # okay
            elif map.changed:
                print "Turning around after map changed"
                r(state, map, dir,depth+1)

        # If we already waited but the map changed, try again
        if move == MOVE_WAIT and map.changed:
            r(state, map, MOVE_WAIT,depth+1)
        # But if we waited and the map didn't change, don't wait again
        elif move == MOVE_WAIT:
            pass
        # else we didn't wait so, go ahead and try waiting
        else:
            r(state, map, MOVE_WAIT,depth+1)

        print "Branch failed at depth", depth
        return 

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
