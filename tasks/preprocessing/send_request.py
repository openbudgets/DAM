"""
    File name: send_request.py
    Author: Maik Lukasche, Tiansi Dong
    Date created: 9/8/2016
    Date last modified: 9/12/2016
    Python Version: 3.5
"""

import requests, datetime, os


class SparqlHelper(object):
    pass


class SparqlCEHelper(SparqlHelper):
    _url = "http://eis-openbudgets.iais.fraunhofer.de/fuseki/sparql"
    _headers = {"Accept": "text/csv"}

    _dict_col2types = {'ID': 'id', 'observation': 'id', 'amount': 'target', 'economicClass': 'nominal',
                       'adminClass': 'nominal',
                       'year': 'nominal',
                       'budgetPhase': 'nominal'}

    _dict_col2model = {'amount': '?observation obeu-measure:amount ?amount2 .',
                       'year': '?observation qb:dataSet/obeu-dimension:fiscalYear ?year .',
                       'budgetPhase': '?observation gr-dimension:budgetPhase ?budgetPhase .',
                       'observation': '?slice qb:observation ?observation .',
                       'economicClass': '?slice gr-dimension:economicClassification ?economicClass .',
                       'adminClass': '?slice gr-dimension:administrativeClassification ?adminClass .'
                       }

    _dict_col2names = {'observation': 'ID', 'amount': 'amount', 'economicClass': 'economicClass',
                       'adminClass': 'adminClass',
                       'year': 'year', 'budgetPhase': 'budgetPhase'}

    _prefixes = [
        "PREFIX obeu-measure:     <http://data.openbudgets.eu/ontology/dsd/measure/>",
        "PREFIX obeu-dimension:   <http://data.openbudgets.eu/ontology/dsd/dimension/>",
        "PREFIX qb:               <http://purl.org/linked-data/cube#>",
        "PREFIX rdfs:             <http://www.w3.org/2000/01/rdf-schema#>",
        "PREFIX gr-dimension: <http://data.openbudgets.eu/ontology/dsd/greek-municipalities/dimension/>"
    ]


    # Helper functions:
    def _create_select(self, datasets, columns, dict_cols2aggr, limit=-1):
        result = "\n".join(SparqlCEHelper._prefixes)
        result += "\nSELECT"
        # columns:
        for col in columns:
            aggregation = dict_cols2aggr.get(col, "")
            if aggregation:
                result += "\n(%s(?%s) AS ?%s)" % (aggregation, col, SparqlCEHelper._dict_col2names[col])
            else:
                result += "\n?%s" % col
        # datsets:
        for dataset in datasets:
            result += "\nFROM %s" % dataset
        # where-clause:
        result += "\nWHERE { %s }" % "\n".join([SparqlCEHelper._dict_col2model.get(col, "") for col in columns])
        # groupBy-clause:
        result += "\nGROUP BY %s" % " ".join(["?%s" % col for col in columns if col not in dict_cols2aggr.keys()])
        if limit > -1:
            result += "\nLIMIT " + str(limit)
        return result

    def _create_type_mapping_line(self, csvText):
        lines = csvText.splitlines()
        tokens = lines[0].split(",")
        types = [SparqlCEHelper._dict_col2types[col] for col in tokens]
        return ",".join(types)


    # Send Request:
    def create_csv_for_outlier_text(self, datasets, columns, dict_cols2aggr, limit=-1):
        """Creates a Sparql-Query for the DM-outlier-algorithm of Christiane,
        sends it to the Sparql-endpoint at FHG-server and returns the result in csv as a String.

            :param datasets: list
                list of the datasets which the Sparql-Query will query the results, for example ["<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012>", "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2014>"]
            :param columns: list
                list of columns OBEU-datamodel, for example ["observation", "amount", "economicClass", "adminClass", "year", "budgetPhase"]
            :param dict_cols2aggr: dict
                dictionary containing the mapping between columns and their aggregation for example {"observation": "MIN", "amount": "SUM"}
            :return: str
                the content of the Sparql-Query-result in csv-format as a String
            Raises:
                todo
        """
        query = SparqlCEHelper._create_select(datasets, columns, dict_cols2aggr, limit=limit)
        params = {"query": query}
        req = requests.get(SparqlCEHelper._url, headers=SparqlCEHelper._headers, params=params)
        csvText = req.text
        print('csvText', csvText)
        csvLines = csvText.splitlines()
        csvLines.insert(1, SparqlCEHelper._create_type_mapping_line(csvText))
        return "\n".join(csvLines)


    def create_csv_for_outlier_file(self, datasets, columns, dict_cols2aggr, path_output_folder, limit=-1):
        """Creates a Sparql-Query for the DM-outlier-algorithm of Christiane,
        sends it to the Sparql-endpoint at FHG-server and returns the result in csv as a file named with the current timestamp in the specified folder.

            :param datasets: list
                list of the datasets which the Sparql-Query will query the results, for example ["<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012>", "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2014>"]
            :param columns: list
                list of columns OBEU-datamodel, for example ["observation", "amount", "economicClass", "adminClass", "year", "budgetPhase"]
            :param dict_cols2aggr: dict
                dictionary containing the mapping between columns and their aggregation for example {"observation": "MIN", "amount": "SUM"}
            :param path_output_folder: str
                folder-path as a String where the CSV-file is placed for example /home/mluk
            :return: str
                the absolute file-path as String of the CSV-file which contains the Sparql-Query-result in csv-format
            Raises:
                todo
        """
        csvText = self.create_csv_for_outlier_text(datasets, columns, dict_cols2aggr, limit=limit)
        fileName = str(datetime.datetime.utcnow()).replace(" ", "_").replace(".", "-").replace(":", "-")
        filePath = os.path.join(path_output_folder, "%s.csv" % fileName)
        with open(filePath, 'a') as the_file:
            the_file.write(csvText)
        return filePath


# Tests:
if __name__ == '__main__':
    # Parameters:
    input_cols = ["observation", "amount", "economicClass", "adminClass", "year", "budgetPhase"]
    input_dict_cols2aggr = {"observation": "MIN", "amount": "SUM"}
    input_datasets = ["<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012>",
                      "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013>",
                      "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2014>"]
    SparqlHelperCE = SparqlCEHelper()
    print(SparqlHelperCE._create_select(input_datasets, input_cols, input_dict_cols2aggr, limit = 1))
    #print(create_csv_for_outlier_text(input_datasets, input_cols, input_dict_cols2aggr))
    print(SparqlHelperCE.create_csv_for_outlier_file(input_datasets, input_cols, input_dict_cols2aggr, os.path.expanduser("~"), limit = 1))
