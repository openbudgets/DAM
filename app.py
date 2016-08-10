import os 
from flask import Flask, jsonify, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache
import datasets as ds
import tasks.statistics as statis 
import tasks.outlier_detection as outlier
import tasks.trend_analysis as trend
import tasks.clustering as cluster
import tasks.myutil as mutil

import numpy as np 
import matplotlib.pyplot as plt
import mpld3
import pandas as pd 
import rdflib
from json import dumps, loads 

cache = Cache(config={'CACHE_TYPE':'simple'})
app = Flask(__name__)
cache.init_app(app)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Triples
currentRDFFile = ''

@app.route('/old', methods=['GET','POST'])
def dam():
    return render_template('index-back.html')


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('dam.html')


@app.route('/echo/', methods=['GET'])
def echo():
    ret_data = {"value": request.args.get('echoValue')}
    print(ret_data)
    return jsonify(ret_data)


@app.route('/observe_dim', methods=['GET'])
def get_dimensions_of_observation():
    global currentRDFFile
    cityName = request.args.get('city')
    print(cityName)
    if cityName != 'None':
        rdfDataset = ds.datasets.get(cityName, '')[0]
        currentRDFFile = rdfDataset
        print(rdfDataset) 
        myGraph = rdflib.Graph()
        myGraph.parse(rdfDataset)
        ret_data =  mutil.get_dimensions_of_observations(myGraph)
        return jsonify(result=ret_data)
    else:
        return jsonify(result='')


@app.route('/code_list', methods=['GET'])
def get_code_list_of_dimension():
    global currentRDFFile
    dimName = request.args.get('dim')
    print(dimName, currentRDFFile)
    
    if dimName != '' and currentRDFFile != '': 
        myGraph = rdflib.Graph()
        myGraph.parse(currentRDFFile)
        ret_data = mutil.get_code_list_of_dim(myGraph, dimName)
        return jsonify(result=ret_data)
    else:
        return jsonify(result='')


@app.route('/outlier_detection', methods=['GET'])
#@cache.cached(timeout=50, key_prefix='all_comments')
def do_outlier_detection():  
    print('in outlier detection')
    dataset_name = request.args.get('dataset_name')
    print('dataset name', dataset_name)
    if dataset_name == 'None':
        ret_data = {}
    else:
        ttl_dataset = ds.datasets.get(dataset_name, '')[0]
        dim_list = request.args.get('dim').split(',')
        print(dim_list)
        per = float(request.args.get('per'))/100
        ret_data = outlier.detect_outliers(dtable=ttl_dataset, dim=dim_list, outliers_fraction = per)
    return ret_data


@app.route('/trend_analysis', methods=['GET'])
# @cache.cached(timeout=50, key_prefix='all_comments')
def do_trend_analysis():
    print('in trend analysis')
    dataset_name = request.args.get('dataset_name')
    print('dataset name', dataset_name)
    if dataset_name == 'None':
        ret_data = {}
    else:
        #dim_list = request.args.get('dim').split(',')
        #print(dim_list)
        ret_data = trend.analyse_trend(dtable=dataset_name)
    return ret_data

@app.route('/statistics', methods=['GET'])
def do_statistics():
    dataset_name = request.args.get('dataset_name')
    print('dataset name',dataset_name)
    if dataset_name != 'None':
        ttlDataset = ds.datasets.get(dataset_name, '')[0]
        print(ttlDataset)
        ret_data = statis.perform_statistics(ttlDataset)
    else:
        ret_data = {}
    print(ret_data)
    return ret_data #jsonify(result=ret_data)


@app.route('/clustering', methods=['GET']) 
@cache.cached(timeout=300, key_prefix='all_comments')
def do_clustering(): 
    print("in /clustering") 
    dataset_name = request.args.get('dataset_name')
    print('dataset name', dataset_name)
    if dataset_name != 'None':
        ttlDataset = ds.datasets.get(dataset_name, '')[0]
        dimList = request.args.get('dim').split(',')
        print(ttlDataset,dimList)
        n_clusters = int(request.args.get('n_clusters'))
        ret_data = cluster.clustering(dtable=ttlDataset, dim=dimList, n_clusters = n_clusters) 
    else:
        ret_data = {}
    return ret_data #jsonify(result=ret_data)
    
 
if __name__ == '__main__':
    app.run(debug=true)

