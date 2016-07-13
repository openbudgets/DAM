import rdflib


def construct_data_frame(g,dim=[]): 
    """
    if dim=[], take the whole dimensions
    """
    if dim==[]:
        dim = get_all_dimensions(g)
    qstr_part1 = 'select ?s ' 
    
    return dimLst
    
def str_of_dim_vars(stem):
    pass

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


def get_query_result(g, qstr):
    rlt = []
    qres = g.query(qstr)
    for row in qres:
        rlt.append(row)
    return rlt

def get_query_result_column_n(g, qstr, col=0):
    rlt = []
    qres = g.query(qstr)
    for row in qres:
        rlt.append(row[col])
    return rlt

if __name__ == "__main__":
    rdffile = '../Data/aragon-2006-income.rdf'
    g = rdflib.Graph()
    g.parse(rdffile) 
    for row in get_all_observations(g):
        print(row)