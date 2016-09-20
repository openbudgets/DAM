"""
    File name: preprocessing/util.py
    Author: Tiansi Dong, Maik Lukasche
    Date created: 9/14/2016
    Date last modified: 9/14/2016
    Python Version: 3.5
"""
import os


def ce_from_file_names_query_fuseki_output_csv(filenames, debug=True):
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
        return False