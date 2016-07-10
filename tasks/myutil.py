import rdflib

def get_query_result(g, qstr):
    rlt = []
    qres = g.query(qstr)
    for row in qres:
        rlt.append(row[0])
    return rlt

def get_all_dimensions(g):
    qstr_d = "select distinct ?s where {?s ?p ?o . filter (contains(str(?s), 'dimension'))  }"
    return get_query_result(g, qstr_d)


def get_all_observations(g):
    qstr_o = 'select distinct ?s ?p ?o where {?s ?p ?o. filter(contains(str(?s), "observation"))} order by asc(UCASE(str(?s)))'
    return get_query_result(g, qstr_o)

def get_dimensions_of_observations(g):
    qstr = 'select distinct ?p where {?s ?p ?o. filter(contains(str(?s), "observation") && contains(str(?p), "dimension"))} order by asc(UCASE(str(?s)))'
    return get_query_result(g, qstr)

def get_dimensions_of_observations_from_rdf(rdf):
    g = rdflib.Graph()
    g.parse(rdf)
    return get_dimensions_of_observations(g)

def get_code_list_of_dim(g, dim):
    qstr = 'select distinct ?o where {?s ?p ?o. filter(contains(str(?p), "'+dim+'") && contains(str(?o), "/codelist"))} order by asc(UCASE(str(?o)))'
    return get_query_result(g, qstr)