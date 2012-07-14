import sys
import argparse

from eval import eval
from map import Map
from aggress import aggress
from regress import regress
from gen import gen
from port import svm

def parseArgs():
    parser = argparse.ArgumentParser(description='Amir\'s IFC submission',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-r', '--regress', dest='regress',default=False,
            action='store_true', required=False, help="Regress a solution")

    parser.add_argument('-a', '--aggress', dest='aggress',default=False,
            action='store_true', required=False, help="Aggress a solution")

    parser.add_argument('-s', '--svm', dest='svm',default=False,
            action='store_true', required=False, help="Use an svm")

    parser.add_argument('-e', '--eval', dest='eval',type=str,
            required=False, help="Eval moves")

    parser.add_argument('-g', '--g', dest='gen',type=str,
            required=False, help="Generate training data")


    return parser.parse_args()

def main():
    args = parseArgs()

    if args.gen:
        gen(args.gen)
        return

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
    elif args.aggress:
        print "Aggressing..."
        aggress(map)
    elif args.svm:
        svm(map)
    elif args.eval:
        eval(args.eval, map)

if __name__=="__main__":
    main()
