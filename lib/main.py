import sys
import argparse

from map import Map
from regress import regress

def parseArgs():
    parser = argparse.ArgumentParser(description='Amir\'s IFC submission',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-r', '--regress', dest='regress',default=False,
            action='store_true', required=False, help="Regress a solution")

    return parser.parse_args()

def main():
    args = parseArgs()

    map = Map()

    for line in sys.stdin.readlines():
        line = line.strip()
        map.addLine(line)
    map.init()

    print "Loaded", map.width, "x", map.height
    print map

    if args.regress:
        print "Regressing..."
        regress(map)

if __name__=="__main__":
    main()
