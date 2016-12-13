import os 
from flask import Flask, jsonify, request, url_for, send_from_directory
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache
from rq import Queue
from rq.job import Job
from worker import conn_dm
import datasets as ds
import tasks.postprocessing.util as post_util

import tasks.statistics as statis
import tasks.trend_analysis as trend
import tasks.clustering as cluster
import tasks.myutil as mutil

import preprocessing_dm as ppdm
import outlier_dm

import rdflib
from json import dumps, loads, load

import collections

app = Flask(__name__)

cache = Cache(config={'CACHE_TYPE':'simple'})
cache.init_app(app)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
from models import GraphNames

#q_iais = Queue(connection=conn)
q_dm = Queue(connection=conn_dm)
#q_uep = Queue(connection=conn_uep)


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    return jsonify(links)


@app.route('/')
@app.route('/what-is-this')
def index():
    route = collections.OrderedDict()
    route["what-is-this"]="DAM backend for Indigo"
    route["graph_name"]= "list all graph names"
    route["rule_mining"]= "rule mining request"
    return jsonify(route)


#
# begin of DM routes
#

@app.route('/graph_name', methods=['GET'])
@app.route('/graph_name/<useCache>', methods=['GET'])
def graph_name(useCache='True'):
    nlst = ppdm.get_all_names_of_named_graph(db,  GraphNames, use_cache=useCache)
    return jsonify({'names': nlst})


@app.route('/get_fdp_datasets', methods=['GET'])
def get_fdp_dataset_name():
    nlst = ppdm.list_dataset_name()
    return jsonify({'names': nlst})


@app.route('/codelist', methods=['GET','POST'])
@app.route('/codelist/<useCache>', methods=['GET','POST'])
def code_list_name(useCache='True'):
    nlst = ppdm.get_all_codelists_of_named_graph(db,  GraphNames, use_cache=useCache)
    return jsonify({'codelist': nlst})


@app.route('/dataset', methods=['GET','POST'])
@app.route('/dataset/<useCache>', methods=['GET','POST'])
def dataset_name(useCache='True'):
    nlst = ppdm.get_all_dataset_of_named_graph(db,  GraphNames, use_cache=useCache)
    return jsonify({'dataset': nlst})


@app.route('/time_series', methods=['GET'])
def do_time_series():
    tsdata = request.args.get('tsdata', 'not given')
    prediction_steps = request.args.get('prediction_steps', -1)
    OKFGR_TS = os.environ['OKFGR_TS']
    tskwargs = {'tsdata': tsdata, 'prediction_steps': prediction_steps}
    import okfgr_dm
    job = q_dm.enqueue_call(func=okfgr_dm.dm_okfgr, args=[OKFGR_TS], kwargs=tskwargs, result_ttl=5000)
    res = {
        "jobid": job.get_id(),
        "param": {"tsdata": "<name of the file for time series>",
                  "tsdata_value": tsdata,
                  "tsdata_sample": 'Athens_draft_ts',
                  "prediction_steps": "<number of steps for prediction>",
                  "prediction_value": prediction_steps,
                  "prediction_sample": 4,
                  }
    }
    return jsonify(res)


@app.route('/rule_mining', methods=['GET', 'POST'])
def do_rule_mining():
    csvFile = request.args.get('rmdata', "not given")
    import uep_dm
    job = q_dm.enqueue_call(func=uep_dm.send_request_to_UEP_server, args=[csvFile], result_ttl=5000)
    print('rule_mining in job queue with id:', job.get_id())
    res = {
        "jobid": job.get_id(),
        "param": {"rmdata": "<location of the csv file, which shall be sent to the UEP server>",
                  "value_example": "./Data/esif.csv",
                  "value": csvFile,
                  }
    }
    return jsonify(res)


@app.route('/outlier_detection/LOF', methods=['GET'])
def do_outlier_detection_lof():
    """
    outlier detectin based on LOF (local outlier factor).
    Users choose one or more dataset names, a CSV file as input element will be created, and saved in Data/ directory.
    Output is also a CSV file, and saved in static/output/ directory

    Returns: {jobid = job.get_id()}
    """
    print('in outlier detection LOF')
    tab = request.args.get('tab')
    filename = request.args.get('filename')
    output = request.args.get('output', 'Result')
    if request.args.get('full_output', 'partial') == 'full_output':
        full_output = True
    else:
       full_output = False

    delimiter = request.args.get('delimiter', ',')
    quotechar = request.args.get('quotechar', '|')
    limit = request.args.get('limit', 25000)
    min_population_size = request.args.get('min_population_size', 30)
    threshold = request.args.get('threshold', 3)
    threshold_avg = request.args.get('threshold_avg', 3)
    num_outliers = request.args.get('num_outliers', 25)
    k = request.args.get('k', 5)
    print(filename, output, full_output, delimiter, quotechar, limit, min_population_size, threshold,
              threshold_avg, num_outliers, k)
    """
    get/generate csv using filename
    """
    dataPath =  os.path.abspath(os.path.join(os.path.dirname(__file__), 'Data'))
    inputCSVFileName = ppdm.ce_from_file_names_query_fuseki_output_csv(filename, dataPath, debug=False)
    """
    post processing
    determine the directory where output file shall be saved
    """
    output_path = post_util.get_output_data_path()
    """
    set function parameters
    """
    cekwargs = {'min_population_size':30,
                    'full_output': full_output,
                    'output_path': output_path}
    """
    send to the job queue
    """
    if inputCSVFileName:
        job = q_dm.enqueue_call(func= outlier_dm.detect_outliers_subpopulation_lattice,
                                # CE_outlier.detect_outliers_subpopulation_lattice,
                                    args=[inputCSVFileName], kwargs=cekwargs, result_ttl=5000)
        print('outlier detection with job id:', job.get_id())
    else:
        print('unvalid csv file')
    return jsonify(jobid=job.get_id())



@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
    """
    route to get data-mining result

    Parameters
    ----------
    job_key: a unique key of a data-mining job

    Returns: (1) {"status":"Wait!"}, or (2) a json structure of data-mining result
    -------

    """
    job = Job.fetch(job_key, connection=conn_dm)
    if job.is_finished:
        #
        # job.result shall be stored in User query database
        #
        return jsonify(loads(job.result))
    else:
        return jsonify({"status":"Wait!"})


#
# end of DM routes
#

##
## decorator function which checks whether the data-mining task alreadys cached in Datablase
##
def check_data_mining_request(func, useCache=True):
    def wrapper(func, useCache=useCache):
        if not useCache:
            return func()
        else:
            result = None
            #result = try_get_result_from_db()
            if result == None:
                return func()
            else:
                return result


@app.route('/output/<path:filename>', methods=['GET', 'POST'])
def download_file(filename):
    return send_from_directory(directory='output', filename=filename)



@app.route('/services/<algo_id>/meta', methods=['GET'])
def algo_meta_data(algo_id):
    return get_meta_data_of_algorithm(algo_id)


@app.route('/services', methods=['GET'])
def get_all_services():
    with open('tasks/algo_meta.json') as data_file:
        meta_dic = load(data_file)
        print(meta_dic)
        return jsonify(meta_dic['list'])


def get_meta_data_of_algorithm(algo_id):
    """
    Parameters
    ----------
    algo_id: the id of algorithm. if algo_id == '', returns the list of all ids.

    Returns:
    -------
    """
    with open('tasks/algo_meta.json') as data_file:
        meta_dic = load(data_file)
        print(meta_dic)
    if algo_id == "":
        return meta_dic["list"]
    else:
        info = meta_dic.get(algo_id, '')
        return jsonify(info)

 
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

