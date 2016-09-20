import os 
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache
from rq import Queue
from rq.job import Job
#from worker_3 import conn, conn_uep
from worker import conn_dm
import datasets as ds
import tasks.preprocessing.util as pre_util
import tasks.postprocessing.util as post_util

import tasks.statistics as statis 
import tasks.outlier_detection.outlier_detection as outlier
import tasks.outlier_detection.cengles.OutlierDetection_SubpopulationLattice as CE_outlier
import tasks.trend_analysis as trend
import tasks.clustering as cluster
import tasks.myutil as mutil
import tasks.triplestore_util as tristore

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
#q_iais = Queue(connection=conn)
q_dm = Queue(connection=conn_dm)
#q_uep = Queue(connection=conn_uep)


from models import Triples
currentRDFFile = ''


@app.route('/old', methods=['GET','POST'])
def dam():
    return render_template('index-back.html')

@app.route('/output/<path:filename>', methods=['GET', 'POST'])
def download_file(filename):
    return send_from_directory(directory='output', filename=filename)


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('dam.html')


@app.route('/echo', methods=['GET'])
def echo():
    ret_data = {"value": request.args.get('echoValue')}
    return jsonify(ret_data)


def say_hi(astring):
    return astring


@app.route('/queue/<num>', methods=['GET','POST'])
def test_queue(num):
    if num == '0':
        job = q_dm.enqueue_call(func=say_hi, args=('hello from queue for local jobs',), result_ttl=5000)
        print('test_queue in job queue with id:', job.get_id())
        return job.get_id()
    elif num == '1':
        job = q_dm.enqueue_call(func=say_hi, args=('hello from main queue',), result_ttl=5000)
        print('test_queue in job queue with id:', job.get_id())
        return job.get_id()
    elif num == '2':
        job = q_dm.enqueue_call(func=say_hi, args=('hello from queue for uep jobs',), result_ttl=5000)
        print('test_queue in job queue with id:', job.get_id())
        return job.get_id()
    print('Usage: http://localhost:5000/queue/[0-2]')
    return jsonify({})


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
    job = Job.fetch(job_key, connection=conn_dm)
    if job.is_finished:
        #
        # job.result shall be stored in User query database
        #
        return job.result
    else:
        return "Wait!"


@app.route('/observe_dim', methods=['GET'])
def get_dimensions_of_observation():
    global currentRDFFile
    cityName = request.args.get('city')
    print(cityName)
    rdfDataset = ds.datasets.get(cityName, '')[0]
    currentRDFFile = rdfDataset

    if cityName != 'None' and 'fuseki' not in rdfDataset:
        print('here, really here')

        print(rdfDataset)
        myGraph = rdflib.Graph()
        myGraph.parse(rdfDataset)
        ret_data = mutil.get_dimensions_of_observations(myGraph)

        return jsonify(result=ret_data)
    elif 'fuseki' in rdfDataset:
        ret_data = tristore.get_dimensions_from_triple_store(rdfDataset)
        return jsonify(result=ret_data)
    else:
        return jsonify(result='')


@app.route('/code_list', methods=['GET'])
def get_code_list_of_dimension():
    global currentRDFFile
    dimName = request.args.get('dim')
    print(dimName, currentRDFFile)
    
    if dimName != '' and currentRDFFile != '' and 'fuseki' not in currentRDFFile:

        myGraph = rdflib.Graph()
        myGraph.parse(currentRDFFile)
        ret_data = mutil.get_code_list_of_dim(myGraph, dimName)

        return jsonify(result=ret_data)
    else:
        return jsonify(result='')


@app.route('/outlier_detection', methods=['GET'])
#@cache.cached(timeout=50, key_prefix='all_comments')
def do_outlier_detection():  
    """
    first get the tab information
    if tab == CE:
        get parameter
        create job
        return job_id
    elif tab == TD:
        get parameter
        create job
        return job_id
    elif tb == UEP:
        get parameter
        create job
        return job_id
    Returns {jobid = job.get_id()}
    -------

    """
    print('in outlier detection')
    tab = request.args.get('tab')
    print('tab', tab)
    if tab == '#Outlier_LOF':
        """
        get user input
        """
        filename = request.args.get('filename')
        output = request.args.get('output')
        full_output = request.args.get('full_output')
        delimiter = request.args.get('delimiter')
        quotechar = request.args.get('quotechar')
        limit = request.args.get('limit')
        min_population_size = request.args.get('min_population_size')
        threshold = request.args.get('threshold')
        threshold_avg = request.args.get('threshold_avg')
        num_outliers = request.args.get('num_outliers')
        k = request.args.get('k')
        print(filename, output, full_output, delimiter, quotechar, limit, min_population_size, threshold,
              threshold_avg, num_outliers, k)
        """
        get/generate csv using filename
        """
        inputCSVFileName = pre_util.ce_from_file_names_query_fuseki_output_csv(filename, debug=True)
        """
        post processing
        determine the directory where output file shall be saved
        """
        output_path = post_util.get_output_data_path()
        """
        set function parameters
        """
        cekwargs = {'min_population_size':30, 'output_path': output_path}
        """
        send to the job queue
        """
        if inputCSVFileName:
            job = q_dm.enqueue_call(func=CE_outlier.detect_outliers_subpopulation_lattice,
                                    args=[inputCSVFileName], kwargs=cekwargs, result_ttl=5000)
            print('outlier detection with job id:', job.get_id())
        else:
            print('unvalid csv file')
        return jsonify(jobid=job.get_id())


    elif tab == '#Outlier_OneClassSVM':
        dataset_name = request.args.get('dataset_name')
        print('dataset name', dataset_name)

        if dataset_name != 'None':
            ttl_dataset = ds.datasets.get(dataset_name, '')[0]
            dim_list = request.args.get('dim').split(',')
            print(dim_list)
            per = float(request.args.get('per'))/100
            # ret_data = outlier.detect_outliers(dtable=ttl_dataset, dim=dim_list, outliers_fraction = per)
            mykwargs = {'dtable':ttl_dataset, 'dim':dim_list, 'outliers_fraction':per}
            job = q_dm.enqueue_call(func=outlier.detect_outliers, kwargs=mykwargs, result_ttl=5000)
            print('outlier detection with job id:', job.get_id())
            return jsonify(jobid = job.get_id())



@app.route('/trend_analysis', methods=['GET'])
# @cache.cached(timeout=50, key_prefix='all_comments')
def do_trend_analysis():
    print('in trend analysis')
    dataset_name = request.args.get('dataset_name')
    print('dataset name', dataset_name)
    if dataset_name != 'None':
        #dim_list = request.args.get('dim').split(',')
        #print(dim_list)
        #ret_data = trend.analyse_trend(dtable=dataset_name)
        mykwargs = {'dtable': dataset_name}
        job = q_dm.enqueue_call(func=trend.analyse_trend, kwargs=mykwargs, result_ttl=5000)
        print('performing trend analysis with job id:', job.get_id())
        return jsonify(jobid=job.get_id())
    else:
        return jsonify(jobid = 0)


@app.route('/statistics', methods=['GET'])
def do_statistics():
    dataset_name = request.args.get('dataset_name')
    print('dataset name',dataset_name)
    if dataset_name != 'None':
        ttlDataset = ds.datasets.get(dataset_name, '')[0]
        print(ttlDataset)
        mykwargs = {'dtable': ttlDataset}
        # ret_data = statis.perform_statistics(dtable=ttlDataset)
        job = q_dm.enqueue_call(func=statis.perform_statistics, kwargs=mykwargs, result_ttl=5000)
        print('statistics in job queue with id:', job.get_id())
        return jsonify(jobid=job.get_id())
    else:
        ret_data = {}
        # print(ret_data)
        # return ret_data #jsonify(result=ret_data)
        return jsonify(jobid = 0)


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
        #ret_data = cluster.clustering(dtable=ttlDataset, dim=dimList, n_clusters = n_clusters)
        mykwars = {'dtable': ttlDataset, 'dim': dimList, 'n_clusters':n_clusters}
        job = q_dm.enqueue_call(func=cluster.clustering, kwargs=mykwars, result_ttl=5000)
        print('performing clustering with job id:', job.get_id())
        return jsonify(jobid=job.get_id())
    else:
        #ret_data = {}
        return jsonify(jobid = 0)
    
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

