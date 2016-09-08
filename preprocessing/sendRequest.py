import requests, csv

# Inputs:
datasets = [
    "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012>",
    "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013>",
    "<http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2014>"
]
columns = { "col1":"id", "amount"}
dict_aggregations_columns = {}
prefix_dimension =





url = "http://eis-openbudgets.iais.fraunhofer.de/fuseki/sparql"
headers = { "Accept":"text/csv" }
query = """
    PREFIX obeu-measure:     <http://data.openbudgets.eu/ontology/dsd/measure/>
    PREFIX obeu-dimension:   <http://data.openbudgets.eu/ontology/dsd/dimension/>
    PREFIX qb:               <http://purl.org/linked-data/cube#>
    PREFIX rdfs:             <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX gr-dimension: <http://data.openbudgets.eu/ontology/dsd/greek-municipalities/dimension/>

    SELECT
        (MIN(?observation) AS ?ID)
        (SUM(?amount) AS ?amount)
        ?economicClass
        ?adminClass
        ?year
        ?budgetPhase
    FROM <http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2012>
    FROM <http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2013>
    FROM <http://data.openbudgets.eu/resource/dataset/budget-kilkis-expenditure-2014>
      WHERE {
      ?observation obeu-measure:amount ?amount2 .
      ?observation qb:dataSet/obeu-dimension:fiscalYear ?year .
      ?observation gr-dimension:budgetPhase ?budgetPhase .
      ?slice qb:observation ?observation .
      ?slice gr-dimension:economicClassification ?economicClass .
      ?slice gr-dimension:administrativeClassification ?adminClass .
    }
    GROUP BY ?economicClass ?adminClass ?year ?budgetPhase
    LIMIT 25000"""
params = { "query":query }
req = requests.get(url, headers=headers, params=params)
lines = req.text.splitlines()
types_dict = { 'ID':'id', 'amount':'target', 'economicClass':'nominal', 'adminClass':'nominal', 'year':'nominal', 'budgetPhase':'nominal' }
columns_csv = lines[0].split(",")
columns_types = [ types_dict[column] for column in columns_csv ]
lines.insert(1, ",".join(columns_types))
output = "\n".join(lines)
with open("query_result.csv", "w") as file:
    file.write(output)