import rdflib
import numpy as np
from decimal import *



def simple_stats(rdf):
    items = []
    ylst = []
    g = rdflib.Graph()
    g.parse(rdf)
    
    qstr = "select ?s ?o where {?s obeu-measure:amount ?o . }"
    qres = g.query( qstr  )
    for row in qres.result:
        xvalue = row[0].split('/')[-1];
        yvalue =  float(row[1].toPython());
        items.append({'x':int(xvalue), 'y': yvalue});
        ylst.append(yvalue);
    ymean = np.mean(ylst)
    ystd = np.std(ylst)
    print(items[-1])
    print(len(items));
    return {'d':items,'m':ymean, 's':ystd}
    
