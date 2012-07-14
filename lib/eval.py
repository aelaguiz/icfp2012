from map import *

def calcScore(moveList, map):
    score = 0
    score -= len(moveList)
    score += 25 * map.lams
    if map.done:
        score += 50 * map.lams
    else:
        # Assumption that we'll abort
        score += 25 * map.lams

    print score, " in ", len(moveList), "moves"

def eval(moveString, map):
    #print "Evaluating", moveString

    moveList = []

    for move in moveString:
        print move
        if move == MOVE_ABORT:
            print "Evaluation: Aborted"
            return True

        if not map.valid_move(move):
            print "Evaluation: Invalid move", move
            return False

        map.move(move)
        moveList.append(move)
        print map

        if map.done:
            print "Evaluation: Map over"
            calcScore(moveList,map)
            return True

        if map.died:
            print "Evaluation: Died!"
            return False

    calcScore(moveList,map)
    return False
