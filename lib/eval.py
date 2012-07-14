from map import *

def eval(moveString, map):
    #print "Evaluating", moveString

    for move in moveString:
        if move == MOVE_ABORT:
            print "Evaluation: Aborted"
            return True

        if not map.valid_move(move):
            print "Evaluation: Invalid move", move
            return False

        map.move(move)

        if map.done:
            print "Evaluation: Map over"
            return True

        if map.died:
            print "Evaluation: Died!"
            return False

    return False
