"""
    File name: preprocessing/util.py
    Author: Tiansi Dong, Maik Lukasche
    Date created: 9/14/2016
    Date last modified: 9/14/2016
    Python Version: 3.5
"""
import os
from .send_request import SparqlCEHelper


def ce_from_file_names_query_fuseki_output_csv(filenames, debug=False):
    """
    if debug=True, we just use the already exising csv file
    Parameters
    ----------
    filenames
    debug

    Returns
    -------

    """
    if debug:
        dataPath = os.path.join(os.path.abspath(os.path.dirname(__file__) +'../../..'), 'Data')
        if os.path.isdir(dataPath):
            csvFile = os.path.join(dataPath, 'Kilkis_neu.csv')
            print(csvFile)
            return csvFile
        else:
            print('no such path ', dataPath)
            return False
    else:
        fileNamesLst = filenames.split('+')[1:]
        input_cols = ["observation", "amount", "economicClass", "adminClass", "year", "budgetPhase"]
        input_dict_cols2aggr = {"observation": "MIN", "amount": "SUM"}
        input_datasets = ["<http://data.openbudgets.eu/resource/dataset/"+fn+">" for fn in fileNamesLst]

        path_output_folder = os.path.join(os.path.abspath(os.path.dirname(__file__) +'../../..'), 'Data')
        SparqlHelperCE = SparqlCEHelper()
        csvFile = SparqlHelperCE.create_csv_as_file(input_datasets, input_cols,
                                                    input_dict_cols2aggr, path_output_folder, limit=10000)

        return csvFile