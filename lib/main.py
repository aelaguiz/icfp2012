import sys
import argparse

from map import Map
from regress import regress
from port import svm

def parseArgs():
    parser = argparse.ArgumentParser(description='Amir\'s IFC submission',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-r', '--regress', dest='regress',default=False,
            action='store_true', required=False, help="Regress a solution")

    parser.add_argument('-s', '--svm', dest='svm',default=False,
            action='store_true', required=False, help="Use an svm")

    return parser.parse_args()

def main():
    args = parseArgs()

    map = Map()

    for line in sys.stdin.readlines():
        line = line.rstrip('\n')
        map.addLine(line)
    map.init()

    print "Loaded", map.width, "x", map.height
    print map

    if args.regress:
        print "Regressing..."
        regress(map)
    elif args.svm:
        svm(map)

if __name__=="__main__":
    main()
