


def get_dimensions_from_triple_store(rdfDataset):
    """
    rdfDataset is the name which is (or from which we can get) the name of dataset at the Fuseki server
    this function returns all dimensions of this dataset, in a list of string form

    Parameters
    ----------
    rdfDataset: dataset name

    Returns: a list of string
    -------

    """
    dataSetName = rdfDataset.replace("fuseki-", "")
    graphName = "http://data.openbudgets.eu/resource/datasets/"+dataSetName
    qstr_d = "select distinct ?s from {} where {?s ?p ?o . filter (contains(str(?s), 'dimension'))  }".format(graphName)
    #call curl fuseki func
    result = ['sample_dimension1', 'sample_dimension2', 'sample_dimension3']
    return result