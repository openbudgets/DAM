print(__doc__)


# Code source: Gaël Varoquaux
# Modified for documentation by Jaques Grobler
# License: BSD 3 clause
import rdflib
#import mpld3 not support 3D plotting
import plotly.plotly as py
import plotly.graph_objs as go
import matplotlib.font_manager
from json import dumps, loads 
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from sklearn import datasets
import tasks.myutil as mutil

def clustering(dtable='', dim=[], n_clusters = 2): 
    """
    dtable must be a rdf file
    """
    g = rdflib.Graph()
    print('in clustering function', dtable)
    print(dim)
    g.parse(dtable)
    frame = mutil.construct_data_frame(g, dim=dim, withObservationId = False) 
    frame_norm = (frame - frame.mean()) / (frame.max() - frame.min())
    X = frame_norm.as_matrix()
    print(X)
    estimator = KMeans(n_clusters = n_clusters) 
    estimator.fit(X) 
    labels = estimator.labels_
    print(frame.as_matrix().tolist())
    if len(dim)==2 :
        return dumps({'data': frame.as_matrix().tolist(), 'cluster': labels.tolist()})
    else:
        return  dumps({'data': [], 'cluster': []})
    

def sample_clustering():    
    np.random.seed(5)

    centers = [[1, 1], [-1, -1], [1, -1]]
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target

    estimators = {'k_means_iris_3': KMeans(n_clusters=3)}#,
#                  'k_means_iris_8': KMeans(n_clusters=8),
#                  'k_means_iris_bad_init': KMeans(n_clusters=3, n_init=1,
#                                              init='random')}


    fignum = 1
    for name, est in estimators.items():
        fig = plt.figure(fignum, figsize=(4, 3))
        plt.clf()
        ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)

        plt.cla()
        est.fit(X)
        labels = est.labels_ #clustering results

        ax.scatter(X[:, 3], X[:, 0], X[:, 2], c=labels.astype(np.float))

        ax.w_xaxis.set_ticklabels([])
        ax.w_yaxis.set_ticklabels([])
        ax.w_zaxis.set_ticklabels([])
        ax.set_xlabel('Petal width')
        ax.set_ylabel('Sepal length')
        ax.set_zlabel('Petal length')
        fignum = fignum + 1

        # Plot the ground truth
        fig = plt.figure(fignum, figsize=(4, 3))
        plt.clf()
        ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)

        plt.cla()

    for name, label in [('Setosa', 0),
                    ('Versicolour', 1),
                    ('Virginica', 2)]:
        ax.text3D(X[y == label, 3].mean(),
                  X[y == label, 0].mean() + 1.5,
                  X[y == label, 2].mean(), name,
                  horizontalalignment='center',
                  bbox=dict(alpha=.5, edgecolor='w', facecolor='w'))
    # Reorder the labels to have colors matching the cluster results
    y = np.choose(y, [1, 2, 0]).astype(np.float)
    ax.scatter(X[:, 3], X[:, 0], X[:, 2], c=y)

    ax.w_xaxis.set_ticklabels([])
    ax.w_yaxis.set_ticklabels([])
    ax.w_zaxis.set_ticklabels([])
    ax.set_xlabel('Petal width')
    ax.set_ylabel('Sepal length')
    ax.set_zlabel('Petal length')
    
    plt.show()
    
if __name__ == "__main__":
    sample_clustering()