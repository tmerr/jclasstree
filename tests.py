import jtree


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
        parsed = jtree.parse(data)
        assert parsed.package == ('stuff2',)
        assert parsed.imports == [('stuff',)]
        assert parsed.cls == 'A'
        assert parsed.extends == ('stuff', 'A')
        assert parsed.implements == []

def test_node():
    root = jtree.Node.make_root('root')
    root.extend_children([jtree.Node('childA'), jtree.Node('childB')])
    root.navigate(('childA',)).extend_children([jtree.Node('grandchildA'), jtree.Node('grandchildB')])
    assert root.navigate(('aahaha', 'ha')) == None
    assert root.navigate(()) == root
    assert root.navigate(('childA',)).name == 'childA'
    assert root.navigate(('childB', 'gdasgdsag')) == None
    assert root.navigate(('childA', 'grandchildB')).name == 'grandchildB'
