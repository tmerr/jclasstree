import pprint
import jtree
import sys

print(jtree.build_parser().parseString(sys.argv[1]).asDict())
