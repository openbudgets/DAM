'''
@author: cengels, tdong
'''
from numpy import average
from .Items import Feature, Item
from sys import exit
import os
import plotly
import plotly.plotly as py
from plotly.tools import FigureFactory as FF


def read_input_csv(filename, delimiter=',', quotechar='|', limit=25000):
    
    items = list()
    structure = Structure()
    rowcount = 0    
    
    import csv
    with open(filename) as csvfile:
        dataset = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        features = structure.fill(dataset.__next__(), dataset.__next__())
        for row in dataset:
            if rowcount < limit:
                items.append(create_item(row, rowcount, structure))
                rowcount += 1
            
    return [items, features]


def write_csv(lattice, filename = 'output.csv'):
    import csv
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        csv_header = header(lattice.features, conditions=lattice.conditions())
        writer.writerow(csv_header[0])
        writer.writerow(csv_header[1])
        
        for item in lattice.items:
            writer.writerow(write_item(item, lattice.num_vertices()))
            
            
def header(features, conditions = None, write_condition=False):
    
    '''Features'''
    header1 = ["Item", "Features"]
    header2 = [""]
    for feature in features:
        header1.append("")
        header2.append(feature.__repr__())
    
    '''Target'''
    header1[-1]="Target"    
    header2.append("")
    
    '''Scores'''
    print('conditions ', conditions)
    if conditions:
        header1.append("Scores")
        for condition in conditions:
            header2.append(condition.__repr__())
    else:
        if write_condition:
            header1.append("Condition")
        header1.append("Score")

    for i in range(len(header1) - len(header2)):
        header2.append("")
    
    return [header1, header2]

    
def write_item(item, num_scores = None):    
    row = list()
    row.append(item.item_id.__str__())
    
    '''Features'''
    for feature in item.features:
        row.append(feature.__str__())   
        
    '''Target'''
    row.append(item.target.__str__())     
    
    '''Scores'''
    if (num_scores):
        offset = len(row)
        row.extend([""] * num_scores)
        for score in item.scores:
            row[offset + score[0]] = score[2].__str__()
            
    return row


def write_outlier(lattice, filename = 'outlier.csv', threshold = 3, score_type='all'):
    import csv
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        csv_header = header(lattice.features, write_condition = score_type == 'all')
        writer.writerow(csv_header[0])
        writer.writerow(csv_header[1])
        
        for item in lattice.items:
            if score_type == 'all':
                for score in item.scores:
                    if abs(score[2]) > threshold:
                        row = write_item(item)
                        row.append(score[1])
                        row.append(score[2])
                        writer.writerow(row)
            elif score_type == 'avg_score':
                avg_score = average([abs(score[2]) for score in item.scores])
                if avg_score > threshold:
                    row = write_item(item)
                    row.append(avg_score)
                    writer.writerow(row)
    dir, filename = os.path.split(filename)
    return filename


def write_top_outlier(lattice, filename = 'top_outlier.csv', num_outliers = 25, server_data_path = ''):
    import csv
    if os.path.isdir(server_data_path):
        filename = os.path.join(server_data_path, filename)

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        csv_header = header(lattice.features)
        if len(csv_header) > 1:
            writer.writerow(csv_header[0])
            writer.writerow(csv_header[1])
        else:
            writer.writerow(csv_header[0])
        
        #Calculate average scores.
        avg_scores = [(average([abs(score[2]) for score in item.scores]), item) for item in lattice.items]
        avg_scores.sort(key=getKey, reverse=True)      

        for item in avg_scores[:num_outliers]:
            row = write_item(item[1])
            row.append(item[0])
            writer.writerow(row)
    dir, filename = os.path.split(filename)
    return filename

         
def output_table(lattice, threshold = 3, score_type='all'):
    data = header(lattice.features)
     
    for item in lattice.items:
        if score_type == 'all':
            for score in item.scores:
                if abs(score[2]) > threshold:
                    row = write_item(item)
                    row.append(score[1])
                    row.append(score[2])
                    data.append(row)
        elif score_type == 'avg_score':
            avg_score = average([abs(score[2]) for score in item.scores])
            if avg_score > threshold:
                row = write_item(item)
                row.append(avg_score)
                data.append(row)              
                
    plotly.tools.set_credentials_file(username='ChristianeEngels', api_key='wsvzka3dcb')            
    
    table = FF.create_table(data)
    table.layout.width=1000
    py.iplot(table, filename='output_table')

           
def create_item(row, rowcount, structure):

    if structure.id:
        item_id = structure.id
    else:
        item_id = rowcount
        
    features = list()    
    for feature in structure.features:
        if feature[1] == 'numerical':
            try:
                features.append(float(row[feature[0]]))
            except ValueError:
                features.append('n.a.')
        else:
            features.append(row[feature[0]])
            
    try:
        target = float(row[structure.target])
    except ValueError:
        target = 0.0
        print('ValueError: target = {} in row {}'.format(row[structure.target], rowcount))  
    
    return Item(item_id, features, target)         


class Structure:
    
    def __init__(self):
        self.features = list()
        self.id = None
        self.target = None
        
    def fill(self, header1, header2):

        it = 0
        feature_count = 0
        features = list()
        for feature_type in header2:
            if feature_type == 'id':
                self.id = it
            elif feature_type == 'target':
                self.target = it
            elif feature_type == 'nom' or feature_type == 'nominal':
                self.features.append((it, 'nominal'))
                features.append(Feature(feature_count, 'nominal', header1[it]))
                feature_count += 1
            elif feature_type == 'num' or feature_type == 'numerical':
                self.features.append((it, 'numerical'))
                features.append(Feature(feature_count, 'numerical', header1[it]))
                feature_count += 1
            elif feature_type != 'skip' and feature_type != '' and feature_type != ' ':
                print('--> Undefined feature type: ' + feature_type)
            it += 1
        if self.target == None:
            exit('Error: No target attribute specified.')

        return features
    
    
def getKey(item):
    return item[0]    