'''
@author: cengels
'''

class Item():
    '''
    Class for Items in Outlier Detection.
    Each item has an ID, multiple features (nominal/numerical) + 1 target amount.
    '''
    def __init__(self, item_id, features = None, target = 0.0):
        '''
        Constructor
        '''
        if features is None:
            self.features = list()
        else:    
            self.features = features
        self.item_id = item_id
        self.target = target
        self.scores = list()
    
    def feature_value(self, feature):
        return self.features[feature.feature_id] 

    def add_score(self, score_id, condition, score):
        self.scores.append((score_id, condition, score))
            
    def satisfy(self, condition):
        return condition.check_item(self)        
                        
    def __str__ (self):    
        output = str("item " + str(self.item_id) + ": ")
        count = 1
        for f in self.features:
            output += "feature " + str(count) + ": " + f.__str__() + ",  "
            count += 1
        output += "target: " + str(self.target) + "\n"
        return output
        
    def __repr__ (self):    
        output = str("item " + str(self.item_id))
        #output = str("item " + str(self.item_id) + ": " + str(self.target))
        return output
        
    def __gt__(self, other):
        return self.target > other.target
    
    
class Feature():
    '''   
    Class for modeling features.
    
    feature: identifier, e.g. feature name
    feature_type: either nominal or numerical
    '''    
    def __init__(self, feature_id, feature_type, label = None, description = None):
        self.feature_id = feature_id
        self.feature_type = feature_type
        self.label = label
        self.description = description
        
    def __gt__(self, other):
        return self.feature_id > other.feature_id
    
    def __str__ (self):    
        return str(self.feature_type + "feature : " + self.feature_id.__str__() + ", " + str(self.label) + ", " + str(self.description))
        
    def __repr__ (self):  
        return str(self.label)                
    
    def is_nominal(self):
        return self.feature_type == 'nominal'  
    
    def is_numerical(self):
        return self.feature_type == 'numerical'   
    