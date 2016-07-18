import unittest
import tasks.myutil as util


class QstrTest(unittest.TestCase):
    def test(self):
        self.assertEqual(util.create_str_of_spo_vars('?s', varStems=['?p','?d'], num=4),
                         "?s ?p1 ?d1 . ?s ?p2 ?d2 . ?s ?p3 ?d3 . ?s ?p4 ?d4 . ")
        self.assertEqual(util.create_filter_conditions('?p', dim=["a", "b"]),
                            ' && contains(str(?p1), "a") && contains(str(?p2), "b")')


if __name__ == '__main__':
    unittest.main()



