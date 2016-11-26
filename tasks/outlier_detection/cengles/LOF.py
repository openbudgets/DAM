'''
@author: cengels
'''


class LOF():
    '''
    1D local outlier factor implementation
    '''

    def __init__(self, k=5, max_size=20):
        self.k = k               
        self.max = max_size 
    
    def initialize(self, data): # TD: type of data? : list of measures.
        self.initialize_data(data)
        self.fill_neighbors()        
        
    def initialize_data(self, data): # TD: global variable 'first', type of data?
        self.data = list()
        first = True
        for item in data:
            if first:
                self.data.append(LOF_Item(item))
                first = False
            else:    
                self.data.append(LOF_Item(item, self.data[-1]))
        #Set successors
        for item in self.data:
            if item.pred:
                item.pred.succ = item 
    
    def fill_neighbors(self):
        for item in self.data:
            
            pred = item.pred
            succ = item.succ
            
            #Find k nearest neighbors. #TD: if (not pred) and (not succ) ...  #k < min_population_size
            while len(item.neighbors) < self.k:
                if (not pred) and succ:
                    item.neighbors.append(succ)
                    succ = succ.succ
                elif pred and (not succ):
                    item.neighbors.append(pred)
                    pred = pred.pred
                elif d(item,pred) < d(item,succ):
                    item.neighbors.append(pred)
                    pred = pred.pred
                else: 
                    item.neighbors.append(succ)
                    succ = succ.succ                
                        
            #Add all neighbors in this range
            item.kdist = d(item, item.neighbors[-1])
            while len(item.neighbors) < self.max and pred and d(item, pred) == item.kdist:
                # TD: loop when d(item, pred) == d(item, pred.pred)
                item.neighbors.append(pred)
                pred = pred.pred
            while len(item.neighbors) < self.max and succ and d(item, succ) == item.kdist:
                # TD: loop when d(item,succ) == d(item, succ.succ)
                item.neighbors.append(succ)
                succ = succ.succ      
    
    def scores(self):
        return [A.lof() for A in self.data]
    

class LOF_Item():
    '''
    Data structure for 1D local outlier factor implementation.
    
    value:     1D data point
    pred:      predecessor in ordering
    succ:      successor in ordering
    neighbors: k nearest neighbors
    kdist:     dist to k-nearest neighbor
    get_lrd:       local reachability density
    '''
    
    def __init__(self, value, pred = None, succ = None):
        self.value = value
        self.pred = pred
        self.succ = succ
        self.neighbors = list()
        self.lrd = None
        
    def distk(self, X): #TD kdist not initialized
        return max(self.kdist, d(self, X))    
        
    def get_lrd(self): #TD distk not initialized
        if not self.lrd:
            dist = sum([n.distk(self) for n in self.neighbors])
            if dist == 0:
                dist = 1
            self.lrd = float(len(self.neighbors) / dist)
        return self.lrd
        
    def lof(self):
        result = sum([float(n.get_lrd()) for n in self.neighbors]) / len(self.neighbors) / self.get_lrd()
        return result
        
        
def d(A,B):
    return abs(A.value - B.value)        
        
    
    