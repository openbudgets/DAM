import unittest
import ttl2rdf as ut

class MyTest(unittest.TestCase):
    def test(self):
        self.assertEqual(ut.replace_path_head("/Users/tdong/git/datasets/Aragon/2006/codelist/", 
                                           "/Users/tdong/git/datasets/Aragon/", 
                                           "/Users/tdong/git/DAM/Data/"),
                         "/Users/tdong/git/DAM/Data/Aragon/2006/codelist")



if __name__ == '__main__':
    unittest.main()


