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

def viewport(map, curPos, prevPos, prevMove):
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
                blocks.append(map.get(x,y))
            else:
                blocks.append('X')

    blocks.append(curPos[0])
    blocks.append(curPos[1])
    blocks.append(prevPos[0])
    blocks.append(prevPos[1])
    blocks.append(moveInt(prevMove))
    return blocks
