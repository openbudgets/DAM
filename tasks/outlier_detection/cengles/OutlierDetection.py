'''
@author: cengels
'''

from sklearn.svm.classes import OneClassSVM
from abc import abstractmethod, ABCMeta
from numpy import median, average, mean, std
import rpy2.robjects as ro
from .LOF import LOF


'''Apply the specified outlier detection method on the given vertex of the lattice.'''
def detect_outliers(vertex, method = None, score_id = 0, k=5):
    
    if method == None:
        print("Error: No outlier detection method specified.")
        return
    
    '''Get the relevant data (id + target).'''
    data = [(item.item_id, item.target) for item in vertex.items]
    
    '''Apply the outlier detection method.'''
    
    if method == 'Outlier_LOF':
        classifier = Outlier_LOF(k)
    elif method == 'Outlier_LOF_R':
        classifier = Outlier_LOF_R(k)
    elif method == 'Outlier_OneClassSVM':
        classifier = Outlier_OneClassSVM()
    elif method == 'Outlier_StandardDev':
        classifier = Outlier_StandardDev()
    elif method == 'Outlier_Median':
        classifier = Outlier_Median()
    elif method == 'Outlier_Average':
        classifier = Outlier_Average()  
    else:
        print("Error: Outlier detection method is not correctly specified.")
        return
    #TODO: Detect this automatically        
        
    vertex.scores = normalize_scores(classifier.get_scores(data))
    vertex.score_id = score_id

    '''Set the scores.'''
    it = 0
    for item in vertex.items:
        item.add_score(score_id, vertex.conditions, vertex.scores[it])
        cnd1 = '"http://data.openbudgets.eu/resource/codelist/kae-ota-exodwn-2014/7412"'
        cnd2 =  '"http://reference.data.gov.uk/id/year/2012"'
        if vertex.scores[it] > 1000000 :
            print(score_id, vertex.conditions, vertex.scores[it])
        it += 1
        
        
class OutlierMethod(metaclass=ABCMeta):
    '''
    Abstract class for outlier detection methods.
    '''      
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def execute(self, data):
        pass

    @abstractmethod
    def get_scores(self, data):
        pass        
    
    
       
class Outlier_LOF_R(OutlierMethod):
    '''
    Outlier detection using the local outlier factor (LOF) using the predefined R function .
    '''       
    def __init__(self, k=5):
        self.k = k
        
    def execute(self, data):
        #print("Performing outlier detection using 'Outlier_LOF_R' method.")
        ro.r.library("DMwR")
        lof = ro.r['lofactor']
        self.result = lof(ro.FloatVector([data_point[1] for data_point in data]), self.k)
    
    def get_scores(self, data):
        self.execute(data)
        return self.result    
    
    
class Outlier_LOF(OutlierMethod):
    '''
    Outlier detection using the local outlier factor (LOF) .
    '''       
    def __init__(self, k=5):
        self.classifier = LOF(k)
        
    def execute(self, data):
        #print("Performing outlier detection using 'Outlier_LOF' method.")
        self.classifier.initialize([data_point[1] for data_point in data])
    
    def get_scores(self, data):
        self.execute(data)
        return self.classifier.scores()     
    
    
class Outlier_OneClassSVM(OutlierMethod):    
    '''
    Outlier detection using the predefined sklearn OneClassSVM functionalities.
    '''
    def ___init__(self):
        self.classifer = OneClassSVM()
        
    def execute(self, data):
        #print("Performing outlier detection using 'Outlier_OneClassSVM' method.")
        self.classifier.fit(data)
    
    def get_scores(self, data):
        self.execute(data)
        return self.classifier.decision_function(data)

    
class Outlier_StandardDev(OutlierMethod):    
    '''
    Statistical outlier detection method using the standard deviation.
    Usually, items with score > 2 are considered as outliers.
    '''
    def __init__(self):
        pass
        
    def execute(self, data):
        #print("Performing outlier detection using 'Outlier_StandardDev' method.")
        self.mean = mean([value[1] for value in data])
        self.std = std([value[1] for value in data])
    
    def get_scores(self, data):
        self.execute(data)
        if self.std == 0:
            #all points are equal
            return [0]*len(data)
        return [(value[1] - self.mean)/self.std for value in data]  
  
  
    
class Outlier_Median(OutlierMethod):    
    '''
    Simple outlier detection method using the distance to median as score.
    '''
    def __init__(self):
        pass
        
    def execute(self, data):
        #print("Performing outlier detection using 'Outlier_Median' method.")
        self.median = median([value[1] for value in data])
    
    def get_scores(self, data):
        self.execute(data)
        return [value[1] - self.median for value in data]
    
    
class Outlier_Average(OutlierMethod):    
    '''
    Simple outlier detection method using the distance to average as score.
    '''
    def __init__(self):
        pass
        
    def execute(self, data):
        #print("Performing outlier detection using 'Outlier_Average' method.")
        self.average = average([value[1] for value in data])
    
    def get_scores(self, data):
        self.execute(data)
        return [value[1] - self.average for value in data]    
    

def normalize_scores(scores, score_range = None):
    scale_factor = max(abs(max(scores)), abs(min(scores)))
    if scale_factor == 0:
        return scores
    elif score_range == '0-1':
        return [abs(score)/scale_factor for score in scores]
    elif score_range == '-1-1':
        return [score/scale_factor for score in scores]    
    else:
        return scores