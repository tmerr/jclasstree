import jclasstree


fpaths = [
    './testfiles/stuff/A.java',
    './testfiles/stuff/B.java',
    './testfiles/stuff/C.java',
    './testfiles/stuff/D.java',
    './testfiles/stuff2/AA.java',
    './testfiles/stuff2/A.java',
    './testfiles/stuff2/B.java'
]

fully_qualified = {
    ('stuff', 'A'),
    ('stuff', 'B'),
    ('stuff2', 'AA'),
    ('stuff2', 'A'),
    ('stuff2', 'B')
}

def test_parser():
    with open('./testfiles/stuff2/A.java') as f:
        data = f.read()
        parsed = jclasstree.parse(data)
        assert parsed.package == ('stuff2',)
        assert parsed.imports == [('stuff',)]
        assert parsed.name == 'A'
        assert parsed.extends == ('stuff', 'A')
        assert parsed.thetype == 'class'
        #assert parsed.implements == []


def test_node():
    root = jclasstree.Node.make_root()
    root.extend_children([jclasstree.Node('childA'), jclasstree.Node('childB')])
    root.navigate(('childA',)).extend_children([jclasstree.Node('grandchildA'), jclasstree.Node('grandchildB')])
    assert root.navigate(('aahaha', 'ha')) == None
    assert root.navigate(()) == root
    assert root.navigate(('childA',)).name == 'childA'
    assert root.navigate(('childB', 'gdasgdsag')) == None
    assert root.navigate(('childA', 'grandchildB')).name == 'grandchildB'


def test_node_forgepath():
    root = jclasstree.Node.make_root()
    root.forgepath(('one', 'two', 'three', 'four'))
    assert root.navigate(('one', 'two', 'three', 'four'))

def test_node_path():
    root = jclasstree.Node.make_root()
    root.forgepath(('one', 'two', 'three', 'four'))
    four = root.navigate(('one', 'two', 'three', 'four'))
    assert four.path() == ('one', 'two', 'three', 'four')

def test_inheritance():
    inheritance = jclasstree.build_inheritance_tree(fpaths)
    expected_inheritance = {
        ('stuff', 'B'): ('stuff', 'A'),
        ('stuff2', 'AA'): ('stuff2', 'A'),
        ('stuff2', 'A'): ('stuff', 'A'),
        ('stuff2', 'B'): ('stuff', 'B'),
    }
    print(inheritance)
    assert inheritance == expected_inheritance
