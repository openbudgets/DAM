import os
from flask import Flask, jsonify, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
import datasets as ds
import tasks.statistics as statis 
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


@app.route('/clustering', methods=['GET'])
def do_clustering():
    cityName = {"value": request.args.get('city')}
    
    ret_data = {}
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

@app.route('/trend_analysis/<taJson>', methods=['GET'])
def trend_analysis(taJson):
#    print('in app', taJson)
    hstr = '<h1>in trend_analysis with parameter {}</h1>'.format(taJson)
    return hstr
    

def build_plot():
    x_deets = np.random.random(10)
    y_deets = np.random.random(10)
    fig, ax = plt.subplots()
    indata = pd.DataFrame(x_deets, y_deets,)
    indata.plot(ax=ax)
    output = dumps(mpld3.fig_to_dict(fig))
    return output

# Define our URLs and pages.
@app.route('/fig')
def render_plot():
    sample_list = list(np.random.randint(1,99999999,size=1))
    dict_of_plots = list()
    for i in sample_list:
        single_chart = dict()
        single_chart['id'] = 'fig_'+str(i)
        single_chart['json'] = build_plot()     
        dict_of_plots.append(single_chart)
    return render_template('plots.html', dict_of_plots=dict_of_plots)#snippet=plot_snippet)

if __name__ == '__main__':
    app.run(debug=true)

