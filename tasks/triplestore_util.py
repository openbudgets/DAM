


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
    result = ['sample_dimension1', 'sample_dimension2', 'sample_dimension3']
    return result