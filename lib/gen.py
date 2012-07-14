from map import *
from port import *

def gen(corpusPath):
    with open(corpusPath, "r") as f:
        lines = f.readlines()
        f.close()

    classes = []
    samples = []

    for line in lines:
        parts = line.split(",")
        mapFile = parts[0].strip()
        route = parts[1].strip()

        print mapFile, route

        (c, s) = genData(mapFile, route)

        classes += c
        samples += s

    with open("svmData.py", "w") as f:
        f.write("classes="+ str(classes)+ "\n")
        f.write("samples="+ str(samples)+ "\n")

    print len(classes)

def genData(mapFile, route):
    with open(mapFile, "r") as f:
        lines = f.readlines()
        f.close()

    map = Map()
    for line in lines:
        line = line.rstrip('\n')
        map.addLine(line)

    map.init()

    print map

    prevMove = MOVE_WAIT
    prevPos = map.robot_pos

    posList = [map.robot_pos]

    classes = []
    samples = []

    for move in route:
        port = viewport(map, map.robot_pos, prevPos, prevMove, posList)

        classes.append(moveInt(move))
        samples += [{ j+1: v for (j,v) in enumerate(port)}]

        map.move(move)

        posList.append(map.robot_pos)
        prevPos = map.robot_pos
        prevMove = move

    return (classes, samples)
