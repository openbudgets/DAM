"""
    File name: send_request.py
    Author: Tiansi Dong, Maik Lukasche
    Date created: 9/12/2016
    Date last modified: 9/12/2016
    Python Version: 3.5
"""

import unittest
import sys
import os
try:
    from ..send_request import SparqlCEHelper
except:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(os.path.abspath(dir_path), '..'))
    from send_request import SparqlCEHelper


"""
csvText ID,amount,economicClass,adminClass,year,budgetPhase
http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013/observation/80.8111/draft,,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/8111,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/80,http://reference.data.gov.uk/id/year/2013,http://data.openbudgets.eu/resource/codelist/budget-phase/draft

/Users/tdong/2016-09-12_13-33-16-510385.csv
"""


class TestSparqlCEHelper(unittest.TestCase):
    def setUp(self):
        self.input_cols = ["observation", "amount", "economicClass", "adminClass", "year", "budgetPhase"]
        self.input_dict_cols2aggr = {"observation": "MIN", "amount": "SUM"}
        self.input_datasets = ["<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012>",
                               "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013>",
                               "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2014>"]
        self.result = result = """PREFIX obeu-measure:     <http://data.openbudgets.eu/ontology/dsd/measure/>
PREFIX obeu-dimension:   <http://data.openbudgets.eu/ontology/dsd/dimension/>
PREFIX qb:               <http://purl.org/linked-data/cube#>
PREFIX rdfs:             <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gr-dimension: <http://data.openbudgets.eu/ontology/dsd/greek-municipalities/dimension/>
SELECT
(MIN(?observation) AS ?ID)
(SUM(?amount) AS ?amount)
?economicClass
?adminClass
?year
?budgetPhase
FROM <http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012>
FROM <http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013>
FROM <http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2014>
WHERE { ?slice qb:observation ?observation .
?observation obeu-measure:amount ?amount2 .
?slice gr-dimension:economicClassification ?economicClass .
?slice gr-dimension:administrativeClassification ?adminClass .
?observation qb:dataSet/obeu-dimension:fiscalYear ?year .
?observation gr-dimension:budgetPhase ?budgetPhase . }
GROUP BY ?economicClass ?adminClass ?year ?budgetPhase
LIMIT 1"""
        self.CEHelper = SparqlCEHelper()

    def test__create_select(self):
        self.assertEqual(self.result,
                         self.CEHelper._create_select(self.input_datasets,
                                                      self.input_cols, self.input_dict_cols2aggr, limit=1))

    @unittest.skip("do not run this")
    def test_create_type_mapping_line(self):
        pass

    @unittest.skip("do not run this")
    def test_create_csv_for_outlier_text(self):
        pass

    @unittest.skip("do not run this")
    def test_create_csv_for_outlier_file(self):
        pass

if __name__ == '__main__':
    unittest.main()