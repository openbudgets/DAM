"""
    File name: postprocessing/util.py
    Author: Maik Lukasche, Tiansi Dong
    Date created: 9/14/2016
    Date last modified: 9/14/2016
    Python Version: 3.5
"""
import os


def get_output_data_path():
    dataPath = os.path.join(os.path.abspath(os.path.dirname(__file__) +'../../..'), 'static/output')
    return dataPath