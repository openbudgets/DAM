import unittest
import ttl2rdf as ut
import create_dataset_choice as cdc

class TestInOutPath(unittest.TestCase):
    def test(self):
        self.assertEqual(ut.replace_path_head("/Users/tdong/git/datasets/Aragon/2006/codelist/", 
                                           "/Users/tdong/git/datasets/Aragon/", 
                                           "/Users/tdong/git/DAM/Data/"),
                         "/Users/tdong/git/DAM/Data/Aragon/2006/codelist")

class TestDatasetChoice(unittest.TestCase):
    def test(self):
        self.assertEqual(ut.cdc("/Users/tdong/git/DAM/Data/"),
                         {"Aragon-All":[""],
                          "Aragon-2006":[""]
                          }
                         )


if __name__ == '__main__':
    unittest.main()


