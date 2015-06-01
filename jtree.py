import os
import re
from ete2 import Tree
from collections import namedtuple
import pyparsing as pp


def genfpaths():
    result = []
    tree = Tree()
    for dirpath, dirs, fnames in os.walk('.'):
        for fname in fnames:
            if fname.endswith('.java'):
                result.append(os.path.join(dirpath, fname))
    return result


def build_parser():
    k_package = pp.Keyword('package')
    k_implements = pp.Keyword('implements')
    k_extends = pp.Keyword('extends')
    k_class = pp.Keyword('class')
    k_import = pp.Keyword('import')
    keyword = k_package | k_implements | k_extends | k_class | k_import

    identifier = pp.NotAny(keyword) + pp.Word(pp.alphanums + '$' + '_' + pp.srange(r'\x00C0-\xFFFF')).setName('identifier')
    identpath = pp.delimitedList(identifier, delim='.')
    package_dec = k_package + identpath('package') + pp.Literal(';')

    importpath = identpath + pp.Optional(pp.Literal('.') + pp.Literal('*'))
    oneimport = importpath.setResultsName('imports', listAllMatches=True)
    imports = pp.Group(pp.ZeroOrMore(k_import + oneimport + pp.Literal(';'))).setResultsName('importlines')

    implements = k_implements + identpath('implements')
    extends = k_extends + pp.delimitedList(identpath('extends'), delim=',')
    class_dec = k_class + identifier('cls') + pp.Optional(extends) + pp.Optional(implements)

    grammar = package_dec + imports + class_dec

    string_literal = pp.nestedExpr('"')
    grammar.ignore(pp.cStyleComment)
    grammar.ignore(string_literal)

    return grammar


parser = build_parser()
def parse(string):
    '''
    Return a ClassInfo object with fields
        package: a list
        imports: a list of lists
        cls: the string name of the class
        extends: a list
        implements: a list of lists

    Or if there is an error parsing, return None.
    '''

    ClassInfo = namedtuple('ClassInfo', ['package', 'imports', 'cls', 'extends', 'implements'])
    try:
        def tuplify(x):
            # working out the return types from the parser is really annoying.
            # this will turn [], '', or None into (,), and a result into a tuple.
            return () if not x else tuple(x.asList())

        parsed = parser.parseString(string)
        package = tuplify(parsed.package)
        imports = [tuplify(x) for x in parsed.importlines.imports]
        cls = tuplify(parsed.cls)[0]
        extends = tuplify(parsed.extends)
        implements = [tuplify(x) for x in parsed.implements]

        return ClassInfo(package, imports, cls, extends, implements)
    except pp.ParseException:
        return None


class Node():
    def __init__(self, name):
        self.name = name
        self.children = []

    @classmethod
    def make_root(cls, name):
        result = cls(name)
        result.parent = None
        return result

    def extend_children(self, children):
        for ch in children:
            ch.parent = self
        self.children.extend(children)

    def navigate(self, path):
        if len(path) == 0:
            return self
        for child in self.children:
            if path[0] == child.name:
                traveled = child.navigate(path[1:])
                if traveled:
                    return traveled
        return None


def buildtree(fpaths):
    namespaces = defaultdict(list)
    classinfos = []
    for fname in fpaths:
        with open(fname, 'r') as f:
            classinfo = parse(f.fread())
            namespaces[classinfo.package].append(classinfo.cls)
            classinfos.append(classinfo)

    # "import x.y.Z" statements are easy to work with: check Z directly against ('x', 'y', 'Z').
    # "import x.y.*" will grab values from namespaces[(x, y)] => [A, B, C, Z]
    
    # key: a class
    # val: (class, edgetype)
    tree = []
    for cls in classinfos:
        # map names in the local namespace to fully qualified ones
        fullyqualified = defaultdict(list)
        for imp in cls.imports:
            if imp[-1] == '*':
                path = imp[:-2]
                if path in namespaces:
                    children = namespaces[path]
                    for child in children:
                        fullyqualified[child].append(path + [child])
            elif len(imp) == 1:
                fullyqualified.append(imp)
            else:
                fullyqualified[imp[-1]] = imp




def run():
    buildtree(genfpaths())


if __name__ == '__main__':
    run()
