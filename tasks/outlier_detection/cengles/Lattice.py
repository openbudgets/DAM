'''
@author: cengels
'''

import copy
from .Condition import NominalCondition, NumericalCondition
from .OutlierDetection import detect_outliers
from numpy import ceil, Infinity, log10, average
from pandas.tools.tile import cut


class Lattice():
    '''
    Lattice class for subpopulation implementation.
    
    "Graph" of vertices, at each vertex ItemSet + corresponding set of conditions
    '''
    def __init__(self, features, items):
        '''
        Constructor
        '''
        self.features = features
        self.items = items
        self.root = Vertex(items)
    
    def num_vertices(self):    
        return self.root.treesize()
        
    '''
    Pruning rules:
    A child vertex is pruned, if
        - the number of items is smaller than min_population_size
        - the number of items is greater than number of parent items * reduction_factor (0 < reduction_factor <= 1.0)
        TODO: if there is no change in the histogram (i.e. there is no information gain)
    '''    
    def generate_subpopulations(self, max_iteration = -1, min_population_size = 5, reduction_factor = 0.9):
        self.root.branch(self.features, 0, max_iteration, min_population_size)            
        
    def detect_outliers(self, method, k):
        it = 0
        for vertex in self.root.get_children():
            detect_outliers(vertex, method, it, k)
            it += 1
        
    def conditions(self):
        conditions = [{}] * self.num_vertices() 
        for vertex in self.root.get_children():
            if(vertex.scores):  
                conditions[vertex.score_id] = vertex.conditions
        return conditions    
        
    def __str__ (self):
        return "root:\n" + self.root.__str__()
            
    def __repr__ (self):
        return "root:\n" + self.root.__repr__() 

#TODO: Implement iterator for lattice and remove get_children().

        
class Vertex():
    '''
    Vertex in the lattice.
    
    items: list of items (reference)
    conditions : list of conditions (copy)
    children: list of vertices
    scores: list of scores
    '''
    def __init__(self, items, conditions = None):
        self.items = items
        self.children = list()
        if conditions is None:
            self.conditions = list()
        else:    
            self.conditions = copy.deepcopy(conditions)
            
    def num_items(self):
        return len(self.items)   
    
    def max_feature(self):
        return max(condition.feature.feature_id for condition in self.conditions)   
    
    def target_values(self):
        return [float(item.target) for item in self.items]    
    
    def treesize(self):
        return sum([child.treesize() for child in self.children]) + 1
  
    def get_children(self):
        res = list()
        res.append(self)
        for child in self.children:
            res.extend(child.get_children())
        return res    
  
    def branch(self, branching_features, iteration = 0, max_iteration = -1, min_population_size = 5, reduction_factor = 0.9):
        if iteration == max_iteration:
            return
        
        '''Generate possible branching conditions based on features/feature values.'''
        conditions = list()       
        
        for feature in branching_features:     
            if feature.is_nominal():
                for value in set([item.feature_value(feature) for item in self.items]):
                    conditions.append(NominalCondition(feature, value))
            elif feature.is_numerical():               
                '''Discretize values and bin ranges as branching condition.'''
                values = [float(item.feature_value(feature)) for item in self.items
                          if item.feature_value(feature) != 'n.a.']
                if len(values) > 1:  
                    if max(values)-min(values) < 0.1:
                        bins = [min(values), average(values), max(values)]
                    else:
                        num_bins = max(int(min(ceil(len(values)/min_population_size), 10)), 2)
                        bins = cut(values, num_bins, retbins=True)[1]
                    bins = [round(b, digits(b)) for b in bins]
                    bins[0] = -Infinity
                    bins[-1] = Infinity
                    for it in range(0,len(bins)-1):                         
                        conditions.append(NumericalCondition(feature, bins[it], bins[it+1]))      

        '''Generate children and branch - or prune.'''        
        for additional_condition in conditions:  
            child_items = [item for item in self.items if item.satisfy(additional_condition)]
            if len(self.items) * reduction_factor > len(child_items) >= min_population_size:
                child_condition = copy.deepcopy(self.conditions)
                child_condition.append(additional_condition)  
                self.children.append(Vertex(child_items, child_condition))
                child_features = [feature for feature in branching_features if feature > additional_condition.feature]
                self.children[-1].branch(child_features, iteration + 1, max_iteration, min_population_size)

                vset = set()
                for i in range(len(child_condition)):
                    vset |= {child_condition[i].value}

                rset = {'"http://data.openbudgets.eu/resource/codelist/kae-ota-administration-2014/30"',
                        '"http://data.openbudgets.eu/resource/codelist/budget-phase/approved"',
                        '"http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/7412"',
                        '"http://reference.data.gov.uk/id/year/2012"'}
                if vset.issubset(rset):
                    for item in self.items:
                        if item.target == 640490.93:
                            print("*self.items*", vset, item)

    def __str__ (self):    
        return "Conditions:\n{}\nItems:\n{}\nChildren:\n{}\n\n".format(
            self.conditions.__str__(), self.items.__str__(), 
            self.children.__str__()
        )
        
    def __repr__ (self):
        return "Conditions:\n{}\nItems:\n{}\nChildren:\n{}\n\n".format(
            self.conditions.__repr__(), self.items.__repr__(), 
            self.children.__repr__()
        )       
        
        
def digits(number):
    if number == 0:
        return 0
    else:
        if number > 1:
            corr = 0.3
        else:
            corr = 0
        return int(-ceil(log10(abs(number/10))-corr))       