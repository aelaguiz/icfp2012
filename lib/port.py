from map import *

def svm(map):
    viewport(map)

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

def blockInt(block):
    if block == ROBOT:
        return 0
    elif block == ROCK:
        return 1
    elif block == EMPTY:
        return 2
    elif block == LAMBDA:
        return 3
    elif block == OPEN_LIFT:
        return 4
    elif block == CLOSED_LIFT:
        return 5
    elif block == EARTH:
        return 6
    else:
        return 7

def viewport(map, curPos, prevPos, prevMove, posList):
    width = 3
    height = 3

    blocks = []

    for x in range(-width,width):
        for y in range(-height,height):
            if x == y == 0:
                continue

            x = x + map.robot_pos[0]
            y = y + map.robot_pos[1]

            if map.valid(x,y):
                # Mark any place we've been with an 8
                if (x,y) in posList:
                    blocks.append(8)
                else:
                    blocks.append(blockInt(map.get(x,y)))
            else:
                blocks.append(blockInt(None))

    blocks.append(curPos[0]-prevPos[0])
    blocks.append(curPos[1]-prevPos[1])
    blocks.append(map.lam_count())
    blocks.append(map.lams)
    return blocks
