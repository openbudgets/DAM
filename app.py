import os
from flask import Flask, jsonify, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
import datasets as ds
import tasks.statistics as statis

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Triples


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')


@app.route('/echo/', methods=['GET'])
def echo():
    ret_data = {"value": request.args.get('echoValue')}
    print(ret_data)
    return jsonify(ret_data)


@app.route('/clustering/', methods=['GET'])
def do_clustering():
    cityName = {"value": request.args.get('city')}
    
    ret_data = {}
    print(ret_data)
    return jsonify(ret_data)

@app.route('/statistics/', methods=['GET', 'POST'])
def do_statistics():
    cityName = request.args.get('city')
    print(cityName)
    if cityName != 'None':
        ttlDataset = ds.datasets.get(cityName, '')[0]
        print(ttlDataset)
        ret_data = statis.simple_stats(ttlDataset)
    else:
        ret_data = {}
    return jsonify(result=ret_data)

@app.route('/trend_analysis/<taJson>', methods=['GET'])
def trend_analysis(taJson):
#    print('in app', taJson)
    hstr = '<h1>in trend_analysis with parameter {}</h1>'.format(taJson)
    return hstr
    


if __name__ == '__main__':
    app.run(debug=true)

