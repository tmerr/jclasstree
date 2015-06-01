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

    identifier = pp.Word(pp.alphanums + '$' + '_' + pp.srange(r'\x00C0-\xFFFF')).setName('identifier')# + pp.NotAny(keywords)

    package_dec = pp.Group(k_package + identifier('package') + pp.Literal(';'))
    implements = k_implements + identifier('interface')
    extends = k_extends + pp.delimitedList(identifier('baseclass'), delim=',')
    class_dec = pp.Group(k_class + identifier('class') + \
                (pp.Optional(extends) + pp.Optional(implements)))

    grammar = pp.Group(pp.SkipTo(package_dec).suppress() + package_dec + pp.SkipTo(class_dec).suppress() + class_dec)
    string_literal = pp.nestedExpr('"')
    grammar.ignore(pp.cStyleComment)
    grammar.ignore(string_literal)

    return grammar

parser = build_parser()

def parse(string):
    '''Return a ClassInfo namedtuple of with fields package, cls, implements, and extends'''
    ClassInfo = namedtuple('ClassInfo', ['package', 'cls', 'extends', 'implements'])
    try:
        parsed = parser.parseString(string)
        return ClassInfo(parsed.get('package'), parsed.get('class'), parsed.get('extends'), parsed.get('implements'))
    except pp.ParseException:
        return None


def package_structure(fpaths):
    '''return a list of valid fully-qualified class names'''
    result = []

    for fpath in fpaths:
        with open(fpath) as f:
            data = f.read()
            packagename = 'default'
            _, ident, _ = ('package' + java_identifier + ';').parseString(data)
            multi | single | package | cls

            m2 = re.search(r'class\s+([^\s])', data)
            if not m2:
                continue
            classname = m2.group(1)

            path = tuple(packagename.split('.') + [classname])
            result.append(path)

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
