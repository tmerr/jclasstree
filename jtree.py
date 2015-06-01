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
    keywords = k_package + k_implements + k_extends + k_class

    identifier = pp.NotAny(keywords) + pp.Word(pp.alphanums + '$' + '_' + pp.srange(r'\x00C0-\xFFFF')).setName('identifier')

    package_dec = k_package + identifier('package') + pp.Literal(';')
    implements = k_implements + identifier('implements')
    extends = k_extends + pp.delimitedList(identifier('extends'), delim=',')
    class_dec = k_class + identifier('cls') + pp.Optional(extends) + pp.Optional(implements)

    grammar = pp.SkipTo(package_dec).suppress() + package_dec + pp.SkipTo(class_dec).suppress() + class_dec
    string_literal = pp.nestedExpr('"')
    grammar.ignore(pp.cStyleComment)
    grammar.ignore(string_literal)

    return grammar


parser = build_parser()
def parse(string):
    '''Return a dict with fields package, class, (maybe) implements, and (maybe) extends'''
    ClassInfo = namedtuple('ClassInfo', ['package', 'cls', 'implements', 'extends'])
    try:
        parsed = parser.parseString(string)
        return ClassInfo(str(parsed.package[0]), str(parsed.cls[0]), str(parsed.implements), str(parsed.extends))
    except pp.ParseException:
        return None


def package_structure(fpaths):
    '''return a list of valid fully-qualified class names'''
    result = []
    for fname in fpaths:
        with open(fname, 'r') as f:
            dct = parse(f.read())
            if dct:
                result.append(tuple(dct.package.split('.') + [dct.cls]))

    return result


def buildtree(fpaths):
    tree = {}
    classnames = []


    namespace = set()


    for fname in fnames:
        namespace = set()
        with open(fname, 'r') as f:
            m = regex.search(r'([^\s])+\s+extends\s+([^\s])+', f.read())
            if m:
                child, parent = m.group(1), m.group(2)
                tree[parent] = child


def run():
    buildtree(genfpaths())


if __name__ == '__main__':
    run()
