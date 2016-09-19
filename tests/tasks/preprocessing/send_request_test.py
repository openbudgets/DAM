"""
    File name: send_request.py
    Author: Tiansi Dong, Maik Lukasch
    Date created: 9/12/2016
    Date last modified: 9/12/2016
    Python Version: 3.5
"""

import unittest
from tasks.preprocessing.send_request import SparqlDummyHelper, SparqlCEHelper
from mock import patch

"""
csvText ID,amount,economicClass,adminClass,year,budgetPhase
http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013/observation/80.8111/draft,,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/8111,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/80,http://reference.data.gov.uk/id/year/2013,http://data.openbudgets.eu/resource/codelist/budget-phase/draft

/Users/tdong/2016-09-12_13-33-16-510385.csv
"""


class SparqlHelperTest(unittest.TestCase):
    def setUp(self):
        self.sparql_helper = SparqlDummyHelper()

    @patch("send_request_test.SparqlDummyHelper._create_sparql_query")
    @patch("send_request_test.SparqlDummyHelper._send_to_sparql_endpoint")
    @patch("send_request_test.SparqlDummyHelper._postprocess_sparql_result")
    @unittest.skip
    def create_csv_as_text_test(self, mock_postprocess_sparql_result, mock_send_to_sparql_endpoint,
                                mock_create_sparql_query):
        # Define Test input:
        mock_create_sparql_query.return_value = """Select ..."""
        mock_send_to_sparql_endpoint.return_value = """a,b,c
        1,2,3"""
        mock_postprocess_sparql_result.return_value = """a,b,c,d
        1,2,3,4"""
        input_cols = ["observation", "amount", "economicClass", "adminClass", "year", "budgetPhase"]
        input_dict_cols2aggr = {"observation": "MIN", "amount": "SUM"}
        input_datasets = ["<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012>",
                          "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013>",
                          "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2014>"]
        # Run Test:
        csv = self.sparql_helper.create_csv_as_text(input_datasets, input_cols, input_dict_cols2aggr)
        # Assert results:
        print("Result: %s" % csv)
        mock_create_sparql_query.assert_called_once_with(input_datasets, input_cols, input_dict_cols2aggr, -1)
        mock_send_to_sparql_endpoint.assert_called_once_with(mock_create_sparql_query.return_value)
        mock_postprocess_sparql_result.assert_called_once_with(mock_send_to_sparql_endpoint.return_value)
        self.assertEqual(csv, mock_postprocess_sparql_result.return_value,
                         "Test result for expected result: %s" % mock_postprocess_sparql_result.return_value)

    @patch("send_request_test.SparqlDummyHelper.create_csv_as_text")
    @patch("send_request_test.SparqlDummyHelper._write_csv_to_file")
    @unittest.skip
    def create_csv_as_file_test(self, mock_write_csv_to_file, mock_create_csv_as_text):
        # Define Test input:
        mock_write_csv_to_file.return_value = "/a/b/c/d/test.csv"
        mock_create_csv_as_text.return_value = """a,b,c,d
        1,2,3,4
        """
        input_cols = ["observation", "amount", "economicClass", "adminClass", "year", "budgetPhase"]
        input_dict_cols2aggr = {"observation": "MIN", "amount": "SUM"}
        input_datasets = ["<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012>",
                          "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013>",
                          "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2014>"]
        input_path_output_folder = "/a/b/c/d"
        input_filename = "test"
        # Run Test:
        file_path = self.sparql_helper.create_csv_as_file(input_datasets, input_cols, input_dict_cols2aggr,
                                                          input_path_output_folder, input_filename)
        # Assert results:
        print("Result: file_path %s" % file_path)
        mock_create_csv_as_text.assert_called_once_with(self.sparql_helper, input_datasets, input_cols,
                                                        input_dict_cols2aggr, -1)
        mock_write_csv_to_file.assert_called_once_with(self.sparql_helper, mock_create_csv_as_text.return_value,
                                                       input_path_output_folder,
                                                       input_filename)
        expected_output_file_path = "%s/%s.csv" % (input_path_output_folder, input_filename)
        print("expected output_file_path : %s" % expected_output_file_path)
        self.assertEqual(file_path, expected_output_file_path,
                         "Test result for expected result: %s" % expected_output_file_path)


class SparqlCEHelperTest(unittest.TestCase):
    def setUp(self):
        self.input_cols = ["observation", "amount", "economicClass", "adminClass", "year", "budgetPhase"]
        self.input_dict_cols2aggr = {"observation": "MIN", "amount": "SUM"}
        self.input_datasets = ["<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012>",
                               "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013>",
                               "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2014>"]
        self.result = """PREFIX obeu-measure:     <http://data.openbudgets.eu/ontology/dsd/measure/>
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
LIMIT 10"""
        self.ce_helper = SparqlCEHelper()

    def create_sparql_query_test(self):
        result = self.ce_helper._create_sparql_query(self.input_datasets, self.input_cols, self.input_dict_cols2aggr,
                                                     10)
        self.assertEqual(result.strip(), result.strip(), "Überprüfung auf Gleichheit")

    def postprocess_sparql_result_test(self):
        input_csv = """ID,amount,economicClass,adminClass, year , budgetPhase
        .1,.3,economicClass,adminClass,year,budgetPhase
http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013/observation/80.8111/draft,49262.9,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/8111,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/80,http://reference.data.gov.uk/id/year/2013,http://data.openbudgets.eu/resource/codelist/budget-phase/draft
http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2014/observation/15.6235.0001/approved,6949.5,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/6235,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/15,http://reference.data.gov.uk/id/year/2014,http://data.openbudgets.eu/resource/codelist/budget-phase/approved
http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012/observation/70.6413/reserved,0.0,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/6413,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/70,http://reference.data.gov.uk/id/year/2012,http://data.openbudgets.eu/resource/dataset/greek-municipalities/codelist/budget-phase/reserved
http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012/observation/70.7331.0000/revised,0.0,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/7331,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/70,http://reference.data.gov.uk/id/year/2012,http://data.openbudgets.eu/resource/codelist/budget-phase/revised
http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013/observation/70.6414/reserved,0.0,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/6414,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/70,http://reference.data.gov.uk/id/year/2013,http://data.openbudgets.eu/resource/dataset/greek-municipalities/codelist/budget-phase/reserved
http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012/observation/25.6114approved,0.0,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/6114,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/25,http://reference.data.gov.uk/id/year/2012,http://data.openbudgets.eu/resource/codelist/budget-phase/approved
http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012/observation/35.6213approved,0.0,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/6213,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/35,http://reference.data.gov.uk/id/year/2012,http://data.openbudgets.eu/resource/codelist/budget-phase/approved"""
        postprocessed_csv = self.ce_helper._postprocess_sparql_result(input_csv)
        expected_input_csv = """ID,amount,economicClass,adminClass,year,budgetPhase
        id,target,nominal,nominal,nominal,nominal
        .1,.3,economicClass,adminClass,year,budgetPhase
        http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013/observation/80.8111/draft,49262.9,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/8111,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/80,http://reference.data.gov.uk/id/year/2013,http://data.openbudgets.eu/resource/codelist/budget-phase/draft
        http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2014/observation/15.6235.0001/approved,6949.5,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/6235,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/15,http://reference.data.gov.uk/id/year/2014,http://data.openbudgets.eu/resource/codelist/budget-phase/approved
        http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012/observation/70.6413/reserved,0.0,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/6413,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/70,http://reference.data.gov.uk/id/year/2012,http://data.openbudgets.eu/resource/dataset/greek-municipalities/codelist/budget-phase/reserved
        http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012/observation/70.7331.0000/revised,0.0,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/7331,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/70,http://reference.data.gov.uk/id/year/2012,http://data.openbudgets.eu/resource/codelist/budget-phase/revised
        http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013/observation/70.6414/reserved,0.0,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/6414,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/70,http://reference.data.gov.uk/id/year/2013,http://data.openbudgets.eu/resource/dataset/greek-municipalities/codelist/budget-phase/reserved
        http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012/observation/25.6114approved,0.0,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/6114,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/25,http://reference.data.gov.uk/id/year/2012,http://data.openbudgets.eu/resource/codelist/budget-phase/approved
        http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012/observation/35.6213approved,0.0,http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/6213,http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/35,http://reference.data.gov.uk/id/year/2012,http://data.openbudgets.eu/resource/codelist/budget-phase/approved"""
        self.assertEqual(postprocessed_csv.replace(" ", ""), expected_input_csv.replace(" ", ""),
                         "Prüfe auf Gleichheit")


if __name__ == '__main__':
    unittest.main()
