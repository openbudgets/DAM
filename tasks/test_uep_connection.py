import requests
import json
import time
import urllib
from pprint import pprint

API_KEY = 'YX48HVaO9bSH18094S4CvEFffF397186ACZ8S3vYRkMLRxMvwOe'
API_URL = 'https://br-dev.lmcloud.vse.cz/easyminercenter/api'

ANTECEDENT_COLUMNS = []
# there can be list of data fields (columns) in the input CSV -
#  if this array is empty, all data fields not included in consequent will be added into antecedent
CONSEQUENT_COLUMNS = ["Technical_Assistance_5"]
# data fields for the consequent
MIN_CONFIDENCE = 0.7
# requested minimal value of confidence
MIN_SUPPORT = 0.1
# requested minimal value of support

CSV_FILE = "../Data/esif.csv"  # path to the CSV file
CSV_SEPARATOR = ";"
CSV_ENCODING = "utf8"

# upload data set - create datasource
headers = {"Accept": "application/json"}
files = {("file", open(CSV_FILE, 'rb'))}
r = requests.post(API_URL + '/datasources?separator=' + urllib.parse.quote(CSV_SEPARATOR) +
                  '&encoding=' + CSV_ENCODING + '&type=limited&apiKey=' + API_KEY, files=files, headers=headers)
datasource_id = r.json()["id"]

# create miner
headers = {'Content-Type': 'application/json', "Accept": "application/json"}
json_data = json.dumps({"name": "TEST MINER", "type": "cloud", "datasourceId": datasource_id})
r = requests.post(API_URL + "/miners?apiKey=" + API_KEY, headers=headers, data=json_data.encode())
miner_id = r.json()["id"]

# preprocess data fields to attributes
headers = {'Content-Type': 'application/json', "Accept": "application/json"}
r = requests.get(API_URL + '/datasources/' + str(datasource_id) + '?apiKey=' + API_KEY, headers=headers)
datasource_columns = r.json()['column']
attributes_columns_map = {}
for col in datasource_columns:
    column = col["name"]
    json_data = json.dumps(
        {"miner": miner_id, "name": column, "columnName": column, "specialPreprocessing": "eachOne"})
    r = requests.post(API_URL + "/attributes?apiKey=" + API_KEY, headers=headers, data=json_data.encode())
    if r.status_code != 201:
        break  # error occured
    attributes_columns_map[column] = r.json()['name']
    # map of created attributes (based on the existing data fields)

# define data mining task
antecedent = []
consequent = []

# prepare antecedent pattern
if len(ANTECEDENT_COLUMNS):
    # add to antecedent only fields defined in the constant
    for column in ANTECEDENT_COLUMNS:
        antecedent.append({"attribute": attributes_columns_map[column]})
else:
    # add to antecedent all fields not used in consequent
    for (column, attribute_name) in attributes_columns_map.items():
        if not(column in CONSEQUENT_COLUMNS):
            antecedent.append({"attribute": attribute_name})

# prepare consequent pattern
for column in CONSEQUENT_COLUMNS:
    consequent.append({"attribute": attributes_columns_map[column]})

    json_data = json.dumps({"miner": miner_id,
                            "name": "Test task",
                            "limitHits": 1000,
                            "IMs": [
                                {
                                    "name": "CONF",
                                    "value": MIN_CONFIDENCE
                                },
                                {
                                    "name": "SUPP",
                                    "value": MIN_SUPPORT
                                }
                            ],
                            "antecedent": antecedent,
                            "consequent": consequent
                            })
# define new data mining task
r = requests.post(API_URL + "/tasks/simple?apiKey=" + API_KEY, headers=headers, data=json_data.encode())
print("create task response code:" + str(r.status_code))
task_id = str(r.json()["id"])

# start task
r = requests.get(API_URL + "/tasks/" + task_id + "/start?apiKey=" + API_KEY, headers=headers)
while True:
    time.sleep(1)
    # check state
    r = requests.get(API_URL + "/tasks/" + task_id + "/state?apiKey=" + API_KEY, headers=headers)
    task_state = r.json()["state"]
    print("task_state:" + task_state)
    if task_state == "solved":
        break
    if task_state == "failed":
        print(CSV_FILE + ": task failed executing")
        break

# export rules in JSON format
headers = {"Accept": "application/json"}
r = requests.get(API_URL + '/tasks/' + task_id + '/rules?apiKey=' + API_KEY, headers=headers)
task_rules = r.json()
pprint(task_rules)

# export of standardized PMML AssociationModel
r = requests.get(API_URL + '/tasks/' + task_id + '/pmml?model=associationmodel&apiKey=' + API_KEY)
pmml = r.text

# export of GUHA PMML
r = requests.get(API_URL + '/tasks/' + task_id + '/pmml?model=guha&apiKey=' + API_KEY)
guha_pmml = r.text