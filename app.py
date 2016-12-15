import os 
from flask import Flask, jsonify, request, url_for, send_from_directory
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache
from rq import Queue
from rq.job import Job
from worker import conn_dm
import tasks.postprocessing.util as post_util
import preprocessing_dm as ppdm 

from json import loads, load


app = Flask(__name__)

cache = Cache(config={'CACHE_TYPE':'simple'})
cache.init_app(app)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
from models import GraphNames

q_dm = Queue(connection=conn_dm)


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
    route = {
        "what-is-this": "DAM backend for Indigo",
        "graph_name": "list all graph names",
        "rule_mining": "rule mining request",
         "time_series": "Time series analysis",
        "statistics": "descriptive statistics",
        'site-map': "htt://localhost:5000/site-map",
    }
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


@app.route('/time_series', methods=['GET', 'POST'])
def do_time_series():
    """
    curl --request POST  "http://localhost:5000/time_series?tsdata=Athens_draftts&prediction_steps=4"
    Returns
    -------

    """
    tsdata = request.args.get('tsdata', 'not given')
    prediction_steps = request.args.get('prediction_steps', '-1')
    OKFGR_TS = os.environ['OKFGR_TS']
    tskwargs = {'tsdata': tsdata, 'prediction_steps': prediction_steps}
    import okfgr_dm
    job = q_dm.enqueue_call(func=okfgr_dm.dm_okfgr, args=[OKFGR_TS], kwargs=tskwargs, result_ttl=5000)
    res = {
        "jobid": job.get_id(),
        "param": {"curl" : 'curl --request POST  "http://localhost:5000/time_series?tsdata=Athens_draft_ts&prediction_steps=4"',
                  "remote-endpoint": OKFGR_TS,
                "tsdata": "<name of the file for time series>",
                  "tsdata_value": tsdata,
                  "tsdata_sample": 'Athens_draft_ts',
                  "prediction_steps": "<number of steps for prediction>",
                  "prediction_value": prediction_steps,
                  "prediction_sample": 4,
                  "result link": "http://localhost:5000/results/" + job.get_id()
                  }
    }
    return jsonify(res)


@app.route('/statistics', methods=['GET', 'POST'])
def do_statistics():
    """
    curl --request POST  "http://localhost:5000/statistics?json_data=sample_json_link_openspending&dimensions='functional_classification_2.Function|functional_classification_2.Code'&amount='Revised'&coef.outl=0.8&box.outliers=TRUE&box.wdth=0.2&cor.method='spearman'"
    Returns
    -------

    """
    json_data = request.args.get('json_data', 'not given')
    dimensions = request.args.get('dimensions', '-1')
    OKFGR_SAT = os.environ['OKFGR_SAT']
    amount= request.args.get('amount', 'not given')
    coef_outl=float(request.args.get('coef.outl', 1.5))
    box_outliers =  request.args.get('box.outliers', 'not_given')
    box_wdth=float(request.args.get('box.wdth', 0.2))
    cor_method=request.args.get('cor.method', 'not given')
    satkwargs = {'json_data': json_data, 'dimensions': dimensions, 'amount':amount, 'coef.outl':coef_outl,
                 'box.outliers':box_outliers, 'box.wdth':box_wdth, 'cor.method':cor_method}
    import okfgr_dm
    job = q_dm.enqueue_call(func=okfgr_dm.dm_okfgr, args=[OKFGR_SAT], kwargs=satkwargs, result_ttl=5000)
    res = {
        "jobid": job.get_id(),
        "param": {"curl" : """curl --request POST  "http://localhost:5000/statistics?json_data=sample_json_link_openspending&dimensions='functional_classification_2.Function|functional_classification_2.Code'&amount='Revised'&coef.outl=0.8&box.outliers=TRUE&box.wdth=0.2&cor.method='spearman'""""",
                    "remote-endpoint": OKFGR_SAT,
                    "json_data": "<name of the file for statistic information>",
                  "json_data": json_data,
                  "json_data_sample": 'sample_json_link_openspending',
                  "dimensions": "<number of steps for prediction>",
                  "dimensions_value": dimensions,
                  "dimensions_sample": "functional_classification_2.Function|functional_classification_2.Code",
                  "amount": "<type of the amount>",
                  "amount_value": amount,
                  "amount_sample": "Revised",

                  "coef.outl": "Define the level of boxplot outliers (optional),default is 1.5",
                  "coef.outl_value": coef_outl,
                  "coef.outl_sample": 1.5,

                  "box.outliers": "Define TRUE/FALSE if outliers should be returned (optional),default is TRUE",
                  "box.outliers_value": box_outliers,
                  "box.outliers_sample": True,

                  "box.wdth": "Define box width in boxplot (optional),default is 0.25*sqrt(n)",
                  "box.wdth_value": box_wdth,
                  "box.wdth_sample": "Revised",

                  "cor.method": "Define the correlation method (cor.method), default is 'pearson'",
                  "cor.method_value": cor_method,
                  "cor.method_sample": "'spearman'",

                  "result link": "http://localhost:5000/results/" + job.get_id()
                  }
    }
    return jsonify(res)


@app.route('/rule_mining', methods=['GET', 'POST'])
def do_rule_mining():
    """curl -H "Content-Type:application/json; charset=UTF-8"  --requst POST 'http://localhost:5000/rule_mining?rmdata=./Data/esif.csv'"""
    csvFile = request.args.get('rmdata', "not given")
    import uep_dm
    job = q_dm.enqueue_call(func=uep_dm.send_request_to_UEP_server, args=[csvFile], result_ttl=5000)
    print('rule_mining in job queue with id:', job.get_id())
    res = {
        "jobid": job.get_id(),
        "param": {"rmdata": "<location of the csv file, which shall be sent to the UEP server>",
                  "remote-server": "https://br-dev.lmcloud.vse.cz/easyminercenter/api",
                  "value_example": "./Data/esif.csv",
                  "value": csvFile,
                  "sample curl": """curl -H "Content-Type:application/json; charset=UTF-8"  --requst POST 'http://localhost:5000/rule_mining?rmdata=./Data/esif.csv'""",
                  "result link": "http://localhost:5000/results/" + job.get_id()
                  }
    }
    return jsonify(res)
 

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


@app.route('/output/<path:filename>', methods=['GET', 'POST'])
def download_file(filename):
    """
    output csv file by a data-mining algorithm is saved at static/output directory for downloading
    Parameters
    ----------
    filename

    Returns
    -------

    """
    return send_from_directory(directory='output', filename=filename)


#
# Start of the TO DO part
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

@app.route('/services/<algo_id>/meta', methods=['GET'])
def algo_meta_data(algo_id):
    return get_meta_data_of_algorithm(algo_id)


@app.route('/services', methods=['GET'])
def get_all_services():
    with open('tasks/algo_meta.json') as data_file:
        meta_dic = load(data_file)
        print(meta_dic)
        return jsonify(meta_dic)


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

#
# End of the TO DO part
#

 
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

