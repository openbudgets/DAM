
import os
from SPARQLWrapper import SPARQLWrapper, JSON


try:
    SPARQLEndPoint = os.environ['VIRTUOSO_ENDPOINT']
    FILE_OF_GRAPH_NAMES = os.environ['FILE_OF_GRAPH_NAMES']
except Exception:
    SPARQLEndPoint = "http://eis-openbudgets.iais.fraunhofer.de/virtuoso/sparql"
    FILE_OF_GRAPH_NAMES = "GRAPH_NAMES.txt"


sparql = SPARQLWrapper(SPARQLEndPoint)


###
#  List all names of named-graphs
###
def get_all_names_of_named_graph(db, GraphName, use_cache='True'):
    nlst = []
    names = ""
    if use_cache == 'True':
        nlst=[]
        print('use db cache')
        try:
            for record in db.session.query(GraphName):
                nlst.append(record.gname)
        except:
            print('Error by querying graph names from DB')
        return nlst
    else:
        errors = []
        query_NameOfGraphs = "SELECT Distinct(?g) WHERE { graph ?g {?s ?p ?o .} }"
        sparql.setQuery(query_NameOfGraphs)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        recordId = 0
        for result in results["results"]["bindings"]:
            nm = str(result['g']['value'])
            recordId += 1
            if nm.startswith('http'):
                nlst.append(nm)
                names += nm+"\n"
                try:
                    cur_list = []
                    for record in db.session.query(GraphName):
                        cur_list.append(record.gname)
                    if nm not in cur_list:
                        graphname = GraphName(
                            id= recordId,
                            gname= nm
                        )
                        db.session.add(graphname)
                        db.session.commit()
                    else:
                        print(nm, ' found in da')
                except:
                    errors.append('Unable to add item to GraphNames table')

        with open(FILE_OF_GRAPH_NAMES, 'w') as fh:
            fh.writelines(names)
        return nlst


def get_all_codelists_of_named_graph(db, GraphName, use_cache='True'):
    nlst = get_all_names_of_named_graph(db, GraphName, use_cache = use_cache)
    codelist = []
    for nm in nlst:
        if 'codelist' in nm:
            codelist.append(nm)
    return codelist


def get_all_dataset_of_named_graph(db, GraphName, use_cache='True'):
    nlst = get_all_names_of_named_graph(db, GraphName, use_cache = use_cache)
    datasets = []
    for nm in nlst:
        if 'dataset' in nm:
            datasets.append(nm)
    return datasets



###
#  list content of a named graph
##