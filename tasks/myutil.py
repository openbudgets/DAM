import rdflib
import pandas as pd
import datasets as ds
import numpy as np


def get_dataset_all_temporal(dtable):
    references = [ele for ele in dtable.split('-') if not ele.isdigit()]
    result = []
    for key in ds.datasets.keys():
        lst = [ele for ele in key.split('-') if not ele.isdigit()]
        if set(references).issubset(set(lst)):
            result.append(key)
    return result


def get_time_from_filename(dtable_name):
    lst = [ele for ele in dtable_name.split('-') if ele.isdigit()]
    if len(lst) > 0:
        return int(lst[0])
    else:
        return 0


def get_mean_of_observations(dtable_name):
    rdfDataset = ds.datasets.get(dtable_name, '')[0]
    myGraph = rdflib.Graph()
    myGraph.parse(rdfDataset)
    qstr = "select ?s ?o where {?s obeu-measure:amount ?o . }"
    qres = myGraph.query(qstr)
    ylst = []
    for row in qres.result:
        ylst.append(float(row[1].toPython()))
    return float(np.mean(ylst))


def construct_data_frame(g, dim=[], withObservationId = True):
    """
    if dim=[], take the whole dimensions
    """
    if dim==[]:
        dim = get_all_dimensions(g)
    if  withObservationId :
        qstr = qstr_for_rdf_to_one_table(g, dim=dim, withObservationId = True)
        cols = ['ObservationID'] + dim + ['Measure']
    else:
        qstr = qstr_for_rdf_to_one_table(g, dim=dim, withObservationId = False)
        cols =  dim + ['Measure']
    
    print(qstr, cols)
    matrix = get_query_result_toPython(g, qstr)  
    """
    qrlt is a list of column values -- 'observation-id, dim[0], dim[1], ...,dim[n], 'measure'
    one row of get_query_result(g, qstr) looks as follows
    for example: (rdflib.term.URIRef('http://data.openbudgets.eu/resource/dataset/aragon-2006-income/observation/42'), 
                  rdflib.term.URIRef('http://data.openbudgets.eu/resource/codelist/estructura_financiacion_i_aragon_2006/91003'), 
                  rdflib.term.URIRef('http://data.openbudgets.eu/resource/codelist/estructura_economica_i_aragon_2006/320004'), 
                  rdflib.term.Literal('20000.0', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#decimal'))) 
    one row of get_query_result_toPython(g, qstr) looks as follows
                [42, 91003, 370004, 20000.0]
    """
    data = {}
    i = 0
    for col in cols:
        data[col] = get_column(matrix, i)
        i += 1
    frame = pd.DataFrame(data) 
    return frame 
 

def qstr_for_rdf_to_one_table(g, dim=[], withObservationId = True):
    if withObservationId:
        qstr='select ?s '+ create_str_of_vars('?d', len(dim)) +' ?o   \
             where { '+ create_str_of_spo_vars('?s', varStems=['?p','?d'], num=len(dim)) +'\
                         ?s ?m ?o .  \
                         filter(contains(str(?s), "observation")   '+  create_filter_conditions('?p', dim) +'\
                               && contains(str(?m),  "measure")   \
                                   )  }'
    else:
        qstr='select '+ create_str_of_vars('?d', len(dim)) +' ?o   \
             where { '+ create_str_of_spo_vars('?s', varStems=['?p','?d'], num=len(dim)) +'\
                         ?s ?m ?o .  \
                         filter(contains(str(?s), "observation")   '+  create_filter_conditions('?p', dim) +'\
                               && contains(str(?m),  "measure")   \
                                   )  }'
    return qstr


def create_str_of_spo_vars(headStem, varStems=['?p','?d'], num=1):
    """
    function example: create_str_of_spo_vars(?s, varStems=['?p',?d], 3) ==> '?s ?p1 ?d1 . ?s ?p2 ?d2 . ?s ?p3 ?d3 . '
    """
    rlt = ""
    for i in range(1, num+1):
        rlt +=headStem +' ' + ' '.join(map(lambda s:s+str(i), varStems))+ " . "
    return rlt


def create_filter_conditions(stem, dim):
    """
    function example: create_filter_conditions(?p, dim=["a", "b"]) ==> '&& contains(str(?p1), "a") && contains(str(?p2), "b")'
    """
    rlt = ""
    for i in range(1, len(dim)+1):
        rlt +=' && contains(str(' +stem+str(i)+ '), "'+ dim[i-1] + '")'
    return rlt


def create_str_of_vars(stem, num):
    """
    function example: create_str_of_vars('?d', 2) ==> '?d1 ?d2'
    """
    rlt = ""
    for i in range(1, num+1):
        rlt +=stem+str(i) + " "
    return rlt
        

def get_all_dimensions(g):
    qstr_d = "select distinct ?s where {?s ?p ?o . filter (contains(str(?s), 'dimension'))  }"
    return get_query_result_column_n(g,  qstr_d, col= 0)


def get_all_observation_ids(g):
    qstr_o = 'select distinct ?s ?p ?o where {?s ?p ?o. filter(contains(str(?s), "observation"))} order by asc(UCASE(str(?s)))'
    return get_query_result_column_n(g, qstr_o,col= 0)

def get_all_observations(g):
    qstr_o = 'select distinct ?s ?p ?o where {?s ?p ?o. filter(contains(str(?s), "observation"))} order by asc(UCASE(str(?s)))'
    return get_query_result(g, qstr_o)


def get_dimensions_of_observations(g):
    qstr = 'select distinct ?p where {?s ?p ?o. filter(contains(str(?s), "observation") && contains(str(?p), "dimension"))} order by asc(UCASE(str(?s)))'
    return get_query_result_column_n(g, qstr, col=0)


def get_dimensions_of_observations_from_rdf(rdf):
    g = rdflib.Graph()
    g.parse(rdf)
    return get_dimensions_of_observations(g)


def get_code_list_of_dim(g, dim):
    qstr = 'select distinct ?o where {?s ?p ?o. filter(contains(str(?p), "'+dim+'") && contains(str(?o), "/codelist"))} order by asc(UCASE(str(?o)))'
    return get_query_result_column_n(g, qstr, col=0)


def get_query_result_toPython(g, qstr):
    rlt = [] 
    qres = g.query(qstr) 
    for row in qres: 
        newRow=[]
        for ele in row:
            pele = ele.toPython()  
            if isinstance(pele, str):
                codeStr = pele.split('/')[-1]
                newRow.append(try_to_turn_string_num(codeStr))
            else:
                newRow.append(float(pele))
        rlt.append(newRow) 
    return rlt


def get_query_result(g, qstr):
    rlt = []
    qres = g.query(qstr)
    for row in qres:
        print(row)
        rlt.append(row)
    return rlt


def get_query_result_column_n(g, qstr, col=0):
    rlt = []
    qres = g.query(qstr)
    for row in qres:
        rlt.append(row[col])
    return rlt


def try_to_turn_string_num(aString):
    if is_a_string_int(aString):
        return int(aString)
    elif is_a_string_float(aString):
        return float(aString)
    else:
        return aString


def is_a_string_int(aString):
    try:
        int(aString)
        return True
    except ValueError:
        return False


def is_a_string_float(aString):
    try:
        float(aString)
        return True
    except ValueError:
        return False


def get_column(matrix, i):
    return [row[i] for row in matrix]


if __name__ == "__main__":
    rdffile = '../Data/aragon-2006-income.rdf'
    g = rdflib.Graph()
    g.parse(rdffile)  
    dim = ["fundingClassification", "economicClassification"] 
    frame = construct_data_frame(g, dim)
    print(frame)