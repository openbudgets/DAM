import os 
from flask import Flask, jsonify, request, url_for, send_from_directory
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache
from flask_cors import CORS, cross_origin
from rq import Queue
from rq.job import Job
from worker import conn_dm
import tasks.postprocessing.util as post_util
import preprocessing_dm as ppdm
import outlier_dm

from json import loads, load


app = Flask(__name__)
CORS(app)

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
    welcome = {
        'whoami' : "This is the data analysis mining backend of OpenBudgets.eu",
        'site-map': "htt://localhost:5000/site-map",
    }
    return jsonify(welcome)

@app.route('/sample-data/<dataset>', methods=['GET'])
def get_sample(dataset=''):
    sample_data = None
    try:
        with open('./sample-data/'+dataset) as json_data:
            sample_data = load(json_data)
    except Exception as e:
        print(e)
    return jsonify(sample_data)

#
# begin of DM routes
#

@app.route('/cubes/algo/<algorithm>', methods=['GET'])
@app.route('/cubes/<dataset>/<algorithm>', methods=['GET'])
@app.route('/cubes/<dataset>/algo', methods=['GET'])
def get_algorithm_data(dataset='', algorithm=''):
    """
    /cubes/algo/<algorithm>: return description of algorithm
    /cubes/<dataset>/<algorithm>: return whether algorithm can be applied for dataset
    /cubes/<dataset>/algo: return all algorithms which can be applied for dataset
    Parameters
    ----------
    dataset : dataset name
    algorithm : algorithm name

    Returns
    -------

    """
    if dataset == '' and algorithm != '':
        des = ppdm.get_algo4data(algo=algorithm)
        desIO = ppdm.get_algoIO(algorithm)
        des.update(desIO)
        return jsonify(des)
    elif dataset != '' and algorithm != '':
        dic = ppdm.get_algo4data(algo=algorithm, data=dataset)
        # des = ppdm.get_algo4data(algo=algorithm)
        print(dic)
        # print(des)
        return jsonify(dic)
        # {'decision': dic.get('decision', 'unknown'),
        #            'description': dic['description']})
    elif dataset != '' and algorithm == '':
        algos = ppdm.get_all_algorithms_of(dataset)
        return jsonify(algos)


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
    # json_data = request.args.get('json_data', 'sample_json_link_openspending')
    json_data = request.args.get('BABBAGE_FACT_URI', '')
    if json_data == '':
        json_data = request.args.get('BABBAGE_AGGREGATE_URI', '')
    dimensions = request.args.get('dimensions', '"functional_classification_2.Function|functional_classification_2.Code"')
    OKFGR_SAT = os.environ['OKFGR_SAT']
    amount= request.args.get('amount', '"Revised"')
    coef_outl=float(request.args.get('coef.outl', 1.5))
    box_outliers =  request.args.get('box.outliers', 'TRUE')
    box_wdth=float(request.args.get('box.wdth', 0.2))
    cor_method=request.args.get('cor.method', '"spearman"')
    satkwargs = {'json_data': json_data, 'dimensions': dimensions, 'amount':amount, 'coef.outl':coef_outl,
                 'box.outliers':box_outliers, 'box.wdth':box_wdth, 'cor.method':cor_method}
    import okfgr_dm
    job = q_dm.enqueue_call(func=okfgr_dm.dm_okfgr, args=[OKFGR_SAT], kwargs=satkwargs, result_ttl=5000)
    res = {
        "jobid": job.get_id(),
        "remote-endpoint": OKFGR_SAT,
        "param": {
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
                  },
        "curl": """curl --request POST  "http://localhost:5000/statistics?json_data=sample_json_link_openspending&dimensions='functional_classification_2.Function|functional_classification_2.Code'&amount='Revised'&coef.outl=0.8&box.outliers=TRUE&box.wdth=0.2&cor.method='spearman'""""",
        "result_link": "http://localhost:5000/results/" + job.get_id()
    }
    return jsonify(res)


@app.route('/rule_mining', methods=['GET', 'POST'])
def do_rule_mining():
    """curl -H "Content-Type:application/json; charset=UTF-8"  --requst POST 'http://localhost:5000/rule_mining?rmdata=./Data/esif.csv'"""
    #csvFile = request.args.get('rmdata', "./Data/esif.csv")
    apiURL = "https://br-dev.lmcloud.vse.cz/easyminercenter/api"
    apiKEY = request.args.get('apiKEY',"RuR4r60A18063xYpLcM5A84vyC637539zy14Txx6YerGvoxWLlc")
    taskName="simple"
    outputFormat = 'json'
    antecedentColumns = request.args.get('antecedentColumns', [])
    consequentColumns = request.args.get('consequentColumns', ["amount.sum"])
    minConfidence = request.args.get('minConfidence', 0.7)
    minSupport = request.args.get('minSupport', 0.1)
    csvSeprator = request.args.get('csvSeprator', ",")
    csvEncoding =  request.args.get('csvEncoding',"utf8")


    filename = request.args.get('BABBAGE_FACT_URI', '')
    if filename == '':
        filename = request.args.get('BABBAGE_AGGREGATE_URI', '')
    if filename == '':
        # filename = "http://ws307.math.auth.gr/rudolf/public/api/3/cubes/aragon-2008-income__568a8/facts"
        # filename = "http://ws307.math.auth.gr/rudolf/public/api/3/cubes/budget-kilkis-expenditure-2015__74025/aggregate?drilldown=administrativeClassification.prefLabel%7CeconomicClassification.prefLabel%7CbudgetPhase.prefLabel&aggregates=amount.sum"
        filename = "http://wenxion.net/OBEU/aggregate.json"

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
    # dataPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Data'))
    # if sample == "sample":
    #    inputCSVFileName = ppdm.ce_from_file_names_query_fuseki_output_csv(filename, dataPath, debug=True)
    # elif sample == "real":
    #    inputCSVFileName = ppdm.ce_from_file_names_query_fuseki_output_csv(filename, dataPath, debug=False)
    inputCSVFileName = ppdm.construct_uep_input_csv(filename)
    print(inputCSVFileName)
    """
    post processing
    determine the directory where output file shall be saved
    """
    output_path = post_util.get_output_data_path()
    """
    set function parameters
    """
    cekwargs = {'min_population_size': 30,
                'full_output': full_output,
                'output_path': output_path}
    """
    send to the job queue
    """

    import uep_dm

    job = q_dm.enqueue_call(func=uep_dm.send_request_to_UEP_server, args=[inputCSVFileName,taskName, apiURL,apiKEY,
                                                                          outputFormat,antecedentColumns,
                                                                          consequentColumns,minConfidence,
                                                                          minSupport,csvSeprator,csvEncoding], result_ttl=5000)
    print('rule_mining in job queue with id:', job.get_id())
    res = {
        "jobid": job.get_id(),
        "param": {"rmdata": "<location of the csv file, which shall be sent to the UEP server>",
                  "remote-server": "https://br-dev.lmcloud.vse.cz/easyminercenter/api",
                  "value_example": "./Data/esif.csv",
                  "value": inputCSVFileName,
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

@app.route('/outlier_detection/FQR', methods=['GET', 'POST'])
def do_outlier_detection_uep():

    apiURL = "https://br-dev.lmcloud.vse.cz/easyminercenter/api"
    apiKEY = request.args.get('apiKEY',"RuR4r60A18063xYpLcM5A84vyC637539zy14Txx6YerGvoxWLlc")
    taskName="outlier"
    outputFormat = 'json'
    antecedentColumns = []
    consequentColumns = []
    minConfidence = request.args.get('minConfidence', 0.7)
    minSupport = request.args.get('minSupport', 0.1)
    csvSeprator = request.args.get('csvSeprator', ",")
    csvEncoding =  request.args.get('csvEncoding',"utf8")


    filename = request.args.get('BABBAGE_FACT_URI', '')
    if filename == '':
        filename = request.args.get('BABBAGE_AGGREGATE_URI', '')
    if filename == '':
        filename = "http://wenxion.net/OBEU/aggregate.json"

    output = request.args.get('output', 'Result')
    if request.args.get('full_output', 'partial') == 'full_output':
        full_output = True
    else:
        full_output = False

    """
    get/generate csv using filename
    """
    # dataPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Data'))
    # if sample == "sample":
    #    inputCSVFileName = ppdm.ce_from_file_names_query_fuseki_output_csv(filename, dataPath, debug=True)
    # elif sample == "real":
    #    inputCSVFileName = ppdm.ce_from_file_names_query_fuseki_output_csv(filename, dataPath, debug=False)
    inputCSVFileName = ppdm.construct_uep_input_csv(filename)
    print(inputCSVFileName)
    """
    post processing
    determine the directory where output file shall be saved
    """
    output_path = post_util.get_output_data_path()
    """
    set function parameters
    """
    cekwargs = {'taskName': 30,
                'apiURL': full_output,
                'apiKEY': output_path}
    """
    send to the job queue
    """

    import uep_dm
    if inputCSVFileName:
        job = q_dm.enqueue_call(func=uep_dm.send_request_to_UEP_server, args=[inputCSVFileName,taskName, apiURL,apiKEY,
                                                                          outputFormat,antecedentColumns,
                                                                          consequentColumns,minConfidence,
                                                                          minSupport,csvSeprator,csvEncoding], result_ttl=5000)
        print('outlier_detection in job queue with id:', job.get_id())
    else:
        print('unvalid csv file')
    return jsonify(jobid=job.get_id())


@app.route('/outlier_detection/LOF/<sample>', methods=['GET'])
@app.route('/outlier_detection/LOF', methods=['GET'])
def do_outlier_detection_lof():
    """
    outlier detectin based on LOF (local outlier factor).
    Users choose one or more dataset names, a CSV file as input element will be created, and saved in Data/ directory.
    Output is also a CSV file, and saved in static/output/ directory
    Returns: {jobid = job.get_id()}
    """
    ##
    ## 'filename' shall be the variable storing the link from Indigo!!
    # http://ws307.math.auth.gr/rudolf/public/api/3/cubes/aragon-2008-income__568a8/facts')
    ##

    filename = request.args.get('BABBAGE_FACT_URI', '')
    if filename == '':
        filename = request.args.get('BABBAGE_AGGREGATE_URI', '')
    if filename == '':
        # filename = "http://ws307.math.auth.gr/rudolf/public/api/3/cubes/aragon-2008-income__568a8/facts"
        #filename = "http://ws307.math.auth.gr/rudolf/public/api/3/cubes/budget-kilkis-expenditure-2015__74025/aggregate?drilldown=administrativeClassification.prefLabel%7CeconomicClassification.prefLabel%7CbudgetPhase.prefLabel&aggregates=amount.sum"
        filename = "http://wenxion.net/OBEU/aggregate.json"
        
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
    inputCSVFileName = ppdm.construct_input_csv(filename)
    print(inputCSVFileName)
    """
    post processing
    determine the directory where output file shall be saved
    """
    output_path = post_util.get_output_data_path()
    """
    set function parameters
    """
    cekwargs = {'min_population_size': 30,
                'full_output': full_output,
                'output_path': output_path}
    """
    send to the job queue
    """
    if inputCSVFileName:
        job = q_dm.enqueue_call(func=outlier_dm.detect_outliers_subpopulation_lattice,
                                    args=[inputCSVFileName], kwargs=cekwargs, result_ttl=5000)
        print('outlier detection with job id:', job.get_id())
    else:
        print('unvalid csv file')
    return jsonify(jobid=job.get_id())

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

@app.route('/services/meta/<func>', methods=['GET'])
def dam_meta_data(func):
    return get_meta_data_of_dam(func)


def get_meta_data_of_dam(func):
    """
    Parameters
    ----------
    algo_id: the id of algorithm. if algo_id == '', returns the list of all ids.

    Returns:
    -------
    """
    with open('tasks/dam.json') as data_file:
        meta_dic = load(data_file)
        print(meta_dic)
    if func == "":
        return meta_dic["list"]
    elif func == "all":
        return jsonify(meta_dic)
    else:
        info = meta_dic.get(func, '')
        return jsonify(info)
#
# End of the TO DO part
#

 
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

