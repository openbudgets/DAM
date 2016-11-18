"""
    File name: send_request.py
    Author: Maik Lukasche, Tiansi Dong
    Date created: 9/8/2016
    Date last modified: 9/12/2016
    Python Version: 3.5
"""

import requests
import datetime
import os
from abc import ABCMeta, abstractmethod


class SparqlHelper(metaclass=ABCMeta):
    # Constants:
    __URL = "http://eis-openbudgets.iais.fraunhofer.de/virtuoso/sparql"
    __HEADERS = {"Accept": "text/csv"}

    @abstractmethod
    def _create_sparql_query(self, datasets, columns, dict_cols2aggr={}, limit=-1):
        """
                Must be implemented by the specific subclass.
                This method should return the Sparql-Query which will be send then to the Fhg's Sparql endpoint.
        :param datasets: list of datasets such as ["<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012>",
                          "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013>",
                          "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2014>"]
        :param columns: list of columns which ar selected in the SParql-Query such as ["observation", "amount", "economicClass", "adminClass", "year", "budgetPhase"]
        :param dict_cols2aggr: dictionary containing the mapping from columns to aggregation such as {"observation": "MIN", "amount": "SUM"}
        :param limit: number of rows in the Sparql-query result
        :return: String containing the Sparql-Query which will be sent to the Sparql endpoint
        """
        raise NotImplementedError('call to abstract method _create_sparql_query')

    @abstractmethod
    def _postprocess_sparql_result(self, sparql_result):
        """
        Must be implemented by specific subclasses.
        This method retrieves the Sparql-result retrieved from the Sparql-endpoint as input and should return the csv-input for the DM-algorithm.
        :param sparql_result: query-result in csv format from the Sparql-endpoint
        :return: the csv-input for the DM-algorithm
        """
        raise NotImplementedError('call to abstract method _postprocess_sparql_result')

    def _send_to_sparql_endpoint(self, sparql_query):
        params = {"query": sparql_query}
        response = requests.get(self.__URL, headers=self.__HEADERS, params=params)
        return response.text

    def _write_csv_to_file(self, text, path_output_folder, file_name=None):
        file_name = file_name if file_name else \
            str(datetime.datetime.utcnow()) \
                .replace(" ", "_") \
                .replace(".", "-") \
                .replace(":", "-")
        file_path = os.path.join(path_output_folder, "%s.csv" % file_name)
        print('file_path', file_path)
        with open(file_path, 'a') as file:
            file.write(text)
        return file_path

    def create_csv_as_text(self, datasets, columns, dict_cols2aggr, limit=-1):
        """
        Creates a Sparql-Query & sends it to the Sparql-Fhg-endpoint & returning the result as csv text.
        :return: The CSV Text as String for DataMining Input.
        """
        # (1) Create Sparql-Query: Needs to specified by subclasses
        sparql_query = self._create_sparql_query(datasets, columns, dict_cols2aggr, limit)
        #print("Sparql-Query: %s" % sparql_query)
        # (2) Send Sparql-Query to Endpoint:
        sparql_result = self._send_to_sparql_endpoint(sparql_query)
        #print("Sparql-Query-Result: %s" % sparql_result)
        # (3) Postprocess Sparql-Query-result: Needs to specified by subclasses
        csv_result = self._postprocess_sparql_result(sparql_result)
        print("CSV-Result length: %s" % len(csv_result))
        print("CSV-Result: %s" % csv_result)
        return csv_result

    def create_csv_as_file(self, datasets, columns, dict_cols2aggr, path_output_folder, file_name=None, limit=-1):
        """
        Creates a Sparql-Query & sends it to the Sparql-Fhg-endpoint & returning the result as csv file.
        :return: The CSV file path as String for DataMining Input.
        """
        csv_result = self.create_csv_as_text(datasets, columns, dict_cols2aggr, limit=limit)
        file_path = self._write_csv_to_file(csv_result, path_output_folder, file_name)
        return file_path


class SparqlDummyHelper(SparqlHelper):
    def _create_sparql_query(self, datasets, columns, dict_cols2aggr={}, limit=-1):
        """Implemented by subclasses"""
        pass

    def _postprocess_sparql_result(self, sparql_result):
        """Implemented by subclasses"""
        pass


class SparqlCEHelper(SparqlHelper):
    _DICT_COL_2_TYPES = {'"amount"': 'target', '"economicClass"': 'nominal',
                         '"adminClass"': 'nominal',
                         '"year"': 'nominal',
                         '"budgetPhase"': 'nominal'}

    _DICT_COL_2_ALIAS = {'amount': 'amount2'}

    _DICT_COL_2_MODEL = {'amount': '?observation obeu-measure:amount ?amount2 .',
                         'year': '?observation qb:dataSet/obeu-dimension:fiscalYear ?year .',
                         'budgetPhase': '?observation gr-dimension:budgetPhase ?budgetPhase .',
                         'observation': '?slice qb:observation ?observation .',
                         'economicClass': '?slice ?economicClassification ?economicClass . filter(contains(str(?economicClassification), "economicClassification")) .',
                         'adminClass': '?slice ?administrativeClassification ?adminClass . filter(contains(str(?administrativeClassification), "administrativeClassification"))'
                         #'economicClass': '?slice gr-dimension:economicClassification ?economicClass .',
                         #'adminClass': '?slice gr-dimension:administrativeClassification ?adminClass .'
                         }

    _DICT_COL_2_NAMES = {'observation': 'ID', 'amount': 'amount', 'economicClass': 'economicClass',
                         'adminClass': 'adminClass',
                         'year': 'year', 'budgetPhase': 'budgetPhase'}

    _PREFIXES = [
        "PREFIX obeu-measure:     <http://data.openbudgets.eu/ontology/dsd/measure/>",
        "PREFIX obeu-dimension:   <http://data.openbudgets.eu/ontology/dsd/dimension/>",
        "PREFIX qb:               <http://purl.org/linked-data/cube#>",
        "PREFIX rdfs:             <http://www.w3.org/2000/01/rdf-schema#>",
        "PREFIX gr-dimension: <http://data.openbudgets.eu/ontology/dsd/greek-municipalities/dimension/>"
    ]

    def _create_sparql_query(self, datasets, columns, dict_cols2aggr={}, limit=-1):
        """
            Subclass implementation for Christiane's outlier detection algorithm.
        :param datasets:
        :param columns:
        :param dict_cols2aggr:
        :param limit:
        :return:
        """
        result = "\n".join(SparqlCEHelper._PREFIXES)
        result += "\nSELECT"
        # columns:
        for col in columns:
            aggregation = dict_cols2aggr.get(col, "")
            if aggregation:
                result += "\n(%s(?%s) AS ?%s)" % (aggregation, SparqlCEHelper._DICT_COL_2_ALIAS.get(col, col),
                                                  SparqlCEHelper._DICT_COL_2_NAMES[col])
            else:
                result += "\n?%s" % col
        # datsets:
        for dataset in datasets:
            result += "\nFROM %s" % dataset
        # where-clause:
        result += "\nWHERE { %s }" % "\n".join([SparqlCEHelper._DICT_COL_2_MODEL.get(col, "") for col in columns])
        # groupBy-clause:
        result += "\nGROUP BY %s" % " ".join(["?%s" % col for col in columns if col not in dict_cols2aggr.keys()])
        if limit > -1:
            result += "\nLIMIT " + str(limit)
        print(result)
        return result

    def _postprocess_sparql_result(self, sparql_result):
        """Subclass implementation for Christiane's outlier detection algorithm.
        Adds an additional line for identifiers to the sparql-result for Christiane's outier detection algorithm.

            :param sparql_result: Sparql-result in csv-format
            :return: str
                the input for Christianes outlier detection algorithm
            Raises:
                todo
        """
        csv_lines = sparql_result.splitlines()
        csv_lines.insert(1, SparqlCEHelper._create_type_mapping_line(sparql_result))
        return "\n".join(csv_lines)

    @staticmethod
    def _create_type_mapping_line(csv_text):
        lines = csv_text.splitlines()
        header_items = [item.strip() for item in lines[0].split(",")]
        print(header_items)
        types = [SparqlCEHelper._DICT_COL_2_TYPES.get(item, "") for item in header_items]
        return ",".join(types)


# Tests:
if __name__ == '__main__':
    # Parameters:
    input_cols = ["observation", "amount", "economicClass", "adminClass", "year", "budgetPhase"]
    input_dict_cols2aggr = {"observation": "MIN", "amount": "SUM"}
    input_datasets = ["<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012>",
                      "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013>",
                      "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2014>"]
    sparql_helper_ce = SparqlCEHelper()
    print(sparql_helper_ce.create_csv_as_text(input_datasets, input_cols, input_dict_cols2aggr, limit=100))
    # print(create_csv_for_outlier_text(input_datasets, input_cols, input_dict_cols2aggr))
    # print(sparql_helper_ce.create_csv_as_file(input_datasets, input_cols, input_dict_cols2aggr,
    #                                                 os.path.expanduser("~"), limit=1))
