'''
@author: cengels, tdong
'''

import os
from .Lattice import Lattice
from .InputOutput import write_csv, write_outlier, read_input_csv, write_top_outlier
from _operator import attrgetter
from json import dumps


def detect_outliers_subpopulation_lattice(filename, 
                                          output='Result',
                                          output_path = '',
                                          full_output=False,
                                          delimiter=',',
                                          quotechar='|',
                                          limit=25000,
                                          outlier_method='Outlier_LOF',
                                          #LOF for local outlier factor https://de.wikipedia.org/wiki/Local_Outlier_Factor
                                          min_population_size=30,
                                          threshold=3, 
                                          threshold_avg=3,
                                          num_outliers=25,
                            # Method specific parameters:
                                          k=5):
    
    
    '''Read input and create list of items.'''
    print('Read CSV ...')
    data = read_input_csv(filename, delimiter, quotechar, limit)
    
    items = data[0]
    features = data[1]
    
    #Sort items for LOF calculation.
    items.sort(key=attrgetter('target'))
           
    print(len(items), "items have been created.")
    
    """Create lattice."""
    lattice = Lattice(features, items)
    
    '''Generate subpopulations.'''
    print("Generate subpopulations...")
    lattice.generate_subpopulations(min_population_size=min_population_size)
    print(lattice.num_vertices(), "subpopulations have been created.")
    
    '''Apply outlier detection to the subpopulation lattice.'''
    print("Detect outliers...")
    lattice.detect_outliers(outlier_method, k)
    
    '''InputOutput scores.'''
    print("Write CSV ...")
    if full_output:
        print('full output ', output_path, output)
        write_csv(lattice, os.path.join(output_path, output + '_Scores.csv'))
        filename = write_outlier(lattice, os.path.join(output_path, output + '_Outlier.csv'), threshold)
        write_outlier(lattice, os.path.join(output_path, output + '_Outlier_Avg.csv'), threshold_avg, 'avg_score')
        return dumps({'filename': filename})
    else:
        output_file = output + '_top' + num_outliers.__str__() + '.csv'
        filename = write_top_outlier(lattice, output_file, num_outliers, server_data_path=output_path)
        return dumps({'filename': filename})
    return 0
