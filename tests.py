import inheritance_ete


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
    ('stuff', 'C'),
    ('stuff', 'D'),
    ('stuff2', 'AA'),
    ('stuff2', 'A'),
    ('stuff2', 'B')
}


def test_strip_comments():
    expected = 'abcdefjklmnostuv'

    print(inheritance_ete.strip_comments('abcdef/*ghi*/jklmno//pqr\nstuv'))
    assert False


def test_package_structure():
    #print(inheritance_ete.package_structure(fpaths))
    assert fully_qualified == inheritance_ete.package_structure(fpaths)
