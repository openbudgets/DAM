'''
@author: cengels
'''
from abc import abstractmethod, ABCMeta


class Condition(metaclass=ABCMeta):
    ''' 
    Abstract class for modeling the branching conditions in a lattice.
    A condition is either nominal or numerical.  
    '''
    @abstractmethod
    def __init__(self, feature, value1, value2 = None):
        pass
           
    @abstractmethod 
    def check(self, value):
        pass
    
    def check_item(self, item):
        return self.check(item.feature_value(self.feature))

    
class NominalCondition(Condition):
    '''
    Nominal condition for branching in a lattice.
    Checks "given value == self.value".
    '''
    condition_type = 'Nominal'
    
    def __init__(self, feature, value):
        self.feature = feature
        self.value = value    
        
    def check(self, value):
        return value == self.value
    
    def __str__ (self):    
        return "{} condition:\n     Feature: {}, Value: {}\n".format(
            self.condition_type.__str__(), self.feature.__str__(), self.value.__str__()
            ) 
        
    def __repr__ (self):    
        return "{} = {}".format(
            self.feature.label.__str__(), self.value.__str__()
            )         


class NumericalCondition(Condition):
    '''
    Numerical condition for branching in a lattice.
    Checks "given self.value1 < value <= self.value2".
    '''
    condition_type = 'Numerical'
    
    def __init__(self, feature, value1, value2):
        self.feature = feature
        self.value1 = float(value1)
        self.value2 = float(value2)        
        
    def check(self, value):
        if value == 'n.a.':
            return False
        return self.value1 < float(value) <= self.value2    
    
    def __str__ (self):    
        return "{} condition:\n     Feature: {}, Values: {}\n".format(
            self.condition_type.__str__(), self.feature.__str__(),
            self.value1.__str__(), self.value2.__str__()
            ) 
        
    def __repr__ (self):    
        return "{} < {} <= {}".format(
            self.value1.__str__(), self.feature.label.__str__(), self.value2.__str__()
            )        