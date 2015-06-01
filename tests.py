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


def test_package_structure():
    assert fully_qualified == set(jtree.package_structure(fpaths))
