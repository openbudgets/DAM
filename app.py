import os 
from flask import Flask, jsonify, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
import datasets as ds
import tasks.statistics as statis 
import tasks.outlier_detection as outlier
import tasks.myutil as mutil

import numpy as np 
import matplotlib.pyplot as plt
import mpld3
import pandas as pd 
import rdflib
from json import dumps, loads 

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Triples

myGraph = rdflib.Graph()


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')


@app.route('/echo/', methods=['GET'])
def echo():
    ret_data = {"value": request.args.get('echoValue')}
    print(ret_data)
    return jsonify(ret_data)



@app.route('/observe_dim', methods=['GET'])
def get_dimensions_of_observation():
    cityName = request.args.get('city')
    print(cityName)
    if cityName != 'None':
        rdfDataset = ds.datasets.get(cityName, '')[0]
        print(rdfDataset)
        myGraph.parse(rdfDataset)
        ret_data =  mutil.get_dimensions_of_observations(myGraph)
        return jsonify(result=ret_data)
    else:
        return jsonify(result='')

@app.route('/code_list', methods=['GET'])
def get_code_list_of_dimension():
    dimName = request.args.get('dim')
    print(dimName)
    
    if dimName != '' and myGraph: 
        ret_data =  mutil.get_code_list_of_dim(myGraph, dimName)
        return jsonify(result=ret_data)
    else:
        return jsonify(result='')


@app.route('/outlier_detection', methods=['GET'])
def do_outlier_detection():  
    cityName = request.args.get('city')
    print('city name', cityName)  
    if cityName == 'None':
        ret_data = {}
    else:
        ttlDataset = ds.datasets.get(cityName, '')[0] 
        dimList = request.args.get('dim').split(',')
        print(dimList)
        per = float(request.args.get('per'))/100
        ret_data = outlier.detect_outliers(dtable=ttlDataset, dim=dimList, outliers_fraction = per)
    
    return ret_data

@app.route('/statistics', methods=['GET'])
def do_statistics():
    cityName = request.args.get('city') 
    print(cityName)
    if cityName != 'None':
        ttlDataset = ds.datasets.get(cityName, '')[0]
        print(ttlDataset)
        ret_data = statis.simple_stats(ttlDataset)
    else:
        ret_data = {}
    return ret_data #jsonify(result=ret_data)

@app.route('/clustering', methods=['GET']) 
def do_clustering(): 
    print("in /clustering")
    #mydata = request.get_json()
    cityName = request.args.get('city') 
    print('city Name', cityName)
    
    ret_data = {}
    return ret_data #jsonify(result=ret_data)

@app.route('/trend_analysis/<taJson>', methods=['GET'])
def trend_analysis(taJson):
#    print('in app', taJson)
    hstr = '<h1>in trend_analysis with parameter {}</h1>'.format(taJson)
    return hstr
    
 
if __name__ == '__main__':
    app.run(debug=true)

