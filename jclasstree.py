import os
import re
from ete2 import Tree, TreeNode, TreeStyle, AttrFace, faces
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
    k_enum = pp.Keyword('enum')
    k_annotation_dec = pp.Keyword('@interface')
    k_interface = pp.Keyword('interface')
    k_class = pp.Keyword('class')
    k_import = pp.Keyword('import')
    k_public = pp.Keyword('public')
    k_abstract = pp.Keyword('abstract')
    k_final = pp.Keyword('final')
    keyword = k_package | k_implements | k_extends | k_enum | k_interface | k_class | k_import | k_public | k_abstract | k_final

    identifier = pp.NotAny(keyword) + pp.Word(pp.alphanums + '$' + '_' + pp.srange(r'\x00C0-\xFFFF')).setName('identifier')
    identpath = pp.delimitedList(identifier, delim='.')
    package_dec = pp.Optional(k_package + identpath('package') + pp.Literal(';'))

    importpath = identpath + pp.Optional(pp.Literal('.') + pp.Literal('*'))
    oneimport = importpath.setResultsName('imports', listAllMatches=True)
    imports = pp.Group(pp.ZeroOrMore(k_import + oneimport + pp.Literal(';'))).setResultsName('importlines')

    implements = k_implements + identpath('implements')
    extends = k_extends + pp.delimitedList(identpath('extends'), delim=',')
    type_modifiers = pp.ZeroOrMore(k_public | k_abstract | k_final)('modifiers')
    types = k_class | k_interface | k_enum | k_annotation_dec
    type_dec = type_modifiers + types('thetype') + identifier('name') + pp.Optional(extends) + pp.Optional(implements)

    grammar = package_dec + imports + type_dec

    string_literal = pp.nestedExpr('"')
    annotation = pp.Literal('@') + pp.NotAny('interface') + pp.SkipTo(pp.LineEnd())
    grammar.ignore(pp.cppStyleComment)
    grammar.ignore(string_literal)
    grammar.ignore(annotation)

    return grammar


parser = build_parser()
def parse(string):
    '''
    Return a ClassInfo object with fields
        package: a tuple
        imports: a list of tuples
        thetype: 'class' or 'abstract class' 'interface'
        name: the string name of the class
        extends: a tuple
        implements: a list of tuples

    Will throw an exception if there's an error parsing (common)
    '''

    ClassInfo = namedtuple('TypeInfo', ['package', 'imports', 'thetype', 'name', 'extends', 'implements'])

    def tuplify(x):
        # working out the return types from the parser is really annoying.
        # this will turn [], '', or None into (,), and a result into a tuple.
        return () if not x else tuple(x.asList())

    parsed = parser.parseString(string)
    if not parsed.package:
        package = ('default',)
    else:
        package = tuplify(parsed.package)
    imports = [tuplify(x) for x in parsed.importlines.imports]
    name = tuplify(parsed.name)[0]
    extends = tuplify(parsed.extends)
    #implements = [tuplify(x) for x in parsed.implements]
    implements = []
    thetype = parsed.thetype

    return ClassInfo(package, imports, thetype, name, extends, implements)


class Node():
    def __init__(self, name, data=None):
        self.name = name
        self.children = []
        self.data = data

    @classmethod
    def make_root(cls):
        result = cls('root')
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

    def forgepath(self, path):
        '''creates nodes if they're not there'''
        if len(path) == 0:
            return

        for child in self.children:
            if child.name == path[0]:
                child.forgepath(path[1:])
                return

        newnode = Node(path[0])
        self.extend_children([newnode])
        newnode.forgepath(path[1:])

    def path(self):
        if self.parent == None:
            return ()
        return self.parent.path() + (self.name,)


def get_relationships(fpaths):
    root = Node.make_root()
    classinfos = []
    for fname in fpaths:
        with open(fname, 'r') as f:
            try:
                classinfo = parse(f.read())
                root.forgepath(classinfo.package)
                root.navigate(classinfo.package).extend_children([Node(classinfo.name, data=classinfo)])
                classinfos.append(classinfo)
                print('read {}'.format(fname))
            except pp.ParseException as e:
                print('ignored {}. cause: {:20s}...'.format(fname, e))

    inheritance_parents = {}
    for info in classinfos:
        imported = [root.navigate(info.package)]
        for imp in info.imports:
            if imp[-1] == '*':
                parent = root.navigate(imp[:-2])
                if parent:
                    imported.extend([child.path() for child in parent.children])
            else:
                node = root.navigate(imp)
                if node:
                    imported.append(node)

        thispath = info.package + (info.name,)

        # fully qualify identifiers so they're all absolute
        def qualify(x):
            if len(x) == 1:
                return info.package + x
            return x

        for im in imported:
            qualified_extends = qualify(info.extends)
            package, therest = qualified_extends[:len(info.package)], qualified_extends[len(info.package):]
            try: 
                node = root.navigate(package).navigate(therest)
                if node and len(node.path()) > 0:
                    inheritance_parents[thispath] = node.path()
            except:
                pass

    return inheritance_parents, None


def run():
    style = TreeStyle()
    style.layout_fn = layout
    style.show_leaf_name = False

    tree = Tree(name='Object')
    inheritance_parents, _ = get_relationships(genfpaths())

    forest = []
    for child, parent in inheritance_parents.items():
        pname = '.'.join(parent)
        if all((x.name != parent for x in forest)):
            forest.append(TreeNode(name=pname))
        cname = '.'.join(child)
        if all((x.name != child for x in forest)):
            forest.append(TreeNode(name=cname))

    parentless = set((t.name for t in forest))
    for child, parent in inheritance_parents.items():
        pname = '.'.join(parent)
        cname = '.'.join(child)
        pnode = [t for t in forest if t.name==pname][0]
        cnode = [t for t in forest if t.name==cname][0]
        pnode.add_child(cnode)
        parentless.remove(cname)

    nparentless = [t for t in forest if t.name in parentless]
    for node in nparentless:
        tree.add_child(node)

    tree.show(tree_style=style, name='jclasstree')


def layout(node):
    N = AttrFace("name", fsize=10, fgcolor="black")
    faces.add_face_to_node(N, node, 0)


if __name__ == '__main__':
    run()
