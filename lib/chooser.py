from random import shuffle
from map import *
from port import *

import svm
import svmutil

model = svmutil.svm_load_model("./0B9ZUN.svm")

def moveInt(move):
    if move == MOVE_LEFT:
        return 1
    elif move == MOVE_RIGHT:
        return 2
    elif move == MOVE_UP:
        return 3
    elif move == MOVE_DOWN:
        return 4
    elif move == MOVE_WAIT:
        return 5
    else:
        return 0

def moveFromSvm(svmVal):
    if svmVal == 1:
        return MOVE_LEFT
    elif svmVal == 2:
        return MOVE_RIGHT
    elif svmVal == 3:
        return MOVE_UP
    elif svmVal == 4:
        return MOVE_DOWN
    elif svmVal == 5:
        return MOVE_WAIT

    return None

def askSvmDir(l, hs,d, q,state,map,depth, validMoves):
    lastMove = MOVE_WAIT

    if len(state.moveList) > 0:
        lastMove = state.moveList[-0]

        if lastMove in validMoves:
            return lastMove

    port = viewport(map, map.robot_pos, state.prevPos, lastMove, state.posList)
    #sitDic = { j+1: v for (j,v) in enumerate(port)}
    #print sitDic
    (labels, data) = svmutil.svm_consult([port], model)
    return moveFromSvm(int(labels[0]))

def trySameDir(l, hs,d, q,state,map,depth, validMoves):
    if len(state.moveList) > 0:
        lastMove = state.moveList[-0]

        if lastMove in validMoves:
            return lastMove

def chooseDir(l, hs,d, q,state,map,depth, validMoves, chooserState):
    # If we have no move options
    if len(validMoves) == 0:
        return None

    if not 'svm' in chooserState:
        # First ask the svm what direction to take
        move = askSvmDir(l, hs,d, q,state,map,depth, validMoves)

        chooserState['svm'] = True

        return move

    # Then try to take the move we took last time
    move = trySameDir(l, hs,d, q,state,map,depth, validMoves)
    if move != None:
        return move

    shuffle(validMoves)

    return validMoves[0]

