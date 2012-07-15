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
    return score

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

def evalScore(moveString, origMap, output = False):
    map = Map()
    map.copy(origMap)


    score,moveList = _evalScore(moveString, map)

    if output:
        print "Evaluating", "".join(moveString), "to", score, "in",\
            len(moveList), "moves"
        print origMap
        print map

    return score


def _evalScore(moveString, map):

    moveList = []

    score = 0

    posList = [map.robot_pos]

    for move in moveString:
        score -= 2
        #print move
        if move == MOVE_ABORT:
            #print "Evaluation: Aborted"
            return (score, moveList)

        #if not map.valid_move(move):
            #print "Evaluation: Invalid move", move
            #return (score, moveList)

        lams = map.lams
        map.move(move)
        moveList.append(move)

        if not map.robot_pos in posList:
            posList.append(map.robot_pos)
            score += 1

        if not map.is_doable():
            #print "Map just became unfinishable"
            #print map
            score -= 50
            return (score, moveList)

        if map.lams > lams:
            #print map
            score += 10

            if map.lam_count() == 0:
                score += 20

        if map.changed:
            score += 2

        if map.done:
            #print "Evaluation: Map over"
            return (score + (10*map.lams), moveList)

        if map.died:
            score -= 50

            return (score, moveList) 

    #score += 10
    return (score, moveList)
