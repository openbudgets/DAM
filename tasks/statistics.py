import rdflib
import numpy as np
import matplotlib.pyplot as plt
import mpld3
import pandas as pd
from decimal import *
from json import dumps, loads 
import tasks.myutil as mutil
from collections import Counter


def perform_statistics(dtable=''):
    points=[]
    ylst = []
    title = ''
    ymin = 1000000000
    ymax = 0
    g = rdflib.Graph()
    g.parse(dtable)
    
    qstr = "select ?s ?o where {?s obeu-measure:amount ?o . }"
    qres = g.query( qstr  ) 
    for row in qres.result: 
        xvalue = row[0].split('/')[-1]
        title = '/'.join(row[0].split('/')[:-1])
        yvalue =  float(row[1].toPython())
        points.append([int(xvalue), yvalue])
        ylst.append(yvalue)
        if ymin > yvalue:
            ymin = yvalue
        if ymax < yvalue:
            ymax = yvalue
    ymean = np.mean(ylst)
    ystd = np.std(ylst) 
    ydata = Counter(ylst)
    sorted_by_x = sorted(points, key=lambda ele: ele[0])
    llst = list(zip(*sorted_by_x))
    xlst, ylst = llst[0], llst[1]
    dimlst = mutil.get_dimensions_of_observations(g)
    return dumps({'xlst':xlst,'ylst':ylst, 'mean': ymean, 'std':ystd, 'min': ymin, 'max': ymax, 'dimlst': dimlst})
    
    
def simple_stats(rdf):
    points=[]
    ylst = []
    title = ''
    ymin = 1000000000
    ymax = 0
    g = rdflib.Graph()
    g.parse(rdf)
    
    qstr = "select ?s ?o where {?s obeu-measure:amount ?o . }"
    qres = g.query(qstr)
    for row in qres.result: 
        xvalue = row[0].split('/')[-1]
        title = '/'.join(row[0].split('/')[:-1])
        yvalue =  float(row[1].toPython()) / 1000
        points.append([int(xvalue), yvalue])
        ylst.append(yvalue)
        if ymin > yvalue:
            ymin = yvalue
        if ymax < yvalue:
            ymax = yvalue
    ymean = np.mean(ylst)
    ystd = np.std(ylst) 
    ydata = Counter(ylst)
    
    #return {'d':items,'m':ymean, 's':ystd}
    print(points)
    dimlst = mutil.get_dimensions_of_observations(g)
    output = build_plot(points, Title= title, mean=ymean,  mode=ydata.most_common(), std=ystd, min=ymin, max=ymax)
    return dumps({'fig':output, 'dimlst':dimlst})

    
# Define a function that will return an HTML snippet.
def build_plot(points, Title='no title', mean=0, mode=[], std=0, min=0, max=0):
    print('mode', mode)
    sorted_by_x = sorted(points, key=lambda ele: ele[0])
    llst  = list(zip(*sorted_by_x)) 
    xlst,ylst = llst[0], llst[1]
    fig, ax = plt.subplots()
    indata = pd.DataFrame(np.asarray(ylst),np.asarray(xlst), )
    #indata.plot(ax=ax)  
    labelStr = 'mean = {:06.2f} '.format(mean)
    plt.scatter(xlst, ylst, label=labelStr)
    plt.scatter(xlst[1:2], ylst[1:2], label='mode = {:.2f}'.format(mode[0][0]))
    plt.scatter(xlst[1:2], ylst[1:2], label='std = {:.2f}'.format(std))
    plt.scatter(xlst[1:2], ylst[1:2], label='max value = {:.2f}'.format(max))
    plt.scatter(xlst[1:2], ylst[1:2], label='min value = {:.2f}'.format(min))
    ax.set_title(Title)
    ax.set_xlabel('Observations')
    #ax.yaxis.tick_right()
    ax.yaxis.set_label_position("left")
    # ax.yaxis.set_label_coords(1.05, -0.025)
    ax.set_ylabel('Amount (in Thousand Euro)')  
   
    ax.legend(loc='upper right')
    output = mpld3.fig_to_dict(fig) 
    return output
