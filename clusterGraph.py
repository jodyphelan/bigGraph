#!/usr/bin/python
from sys import argv
import json
import numpy as np
from sklearn import decomposition
from sklearn import cluster
from sklearn.preprocessing import scale
import matplotlib.pyplot as plt
import argparse
import os

#script,method,inFile,outFile = argv
#inFile = "graph.json"


def queryGraph(totalGraph,nodeID):
    tempEdges = filter(lambda x: x["source"]==nodeID or x["target"]==nodeID, totalGraph["edges"])
    nbrID = np.unique(map(lambda x: x["source"], tempEdges) + map(lambda x: x["target"], tempEdges))
    tempNodes = filter(lambda x: x["id"] in nbrID, totalGraph["nodes"])
    return {"nodes":tempNodes,"edges":tempEdges}

def pcaCluster(attr):
    pca = decomposition.PCA()
    pca.fit(attr)
    return pca

def kmeansCluster(attr):
    kmeans = cluster.KMeans(n_clusters=2)
    kmeans.fit(attr)
    return kmeans

def dbscanCluster(attr):
    dbscan = cluster.DBSCAN()
    dbscan.fit(attr)
    return dbscan

clusteringMethods = {"kmeans":kmeansCluster,"dbscan":dbscanCluster}

def runPCA(args):
    inFile = args.graph
    nodeID = int(args.id)
    origGraph = loadGraph(inFile)
    subGraph = queryGraph(origGraph,nodeID)

    attrib = []
    for i in range(len(subGraph["nodes"])):
        tempArr = []
        for k in subGraph["nodes"][i]["attr"]:
            tempArr.append(subGraph["nodes"][i]["attr"][k])
        attrib.append(tempArr)
    attrib = scale(np.array(attrib))
    pca = pcaCluster(attrib)
    pca.n_components = 2
    attrib_reduced = pca.fit_transform(attrib)
    plt.scatter(attrib_reduced[:,0],attrib_reduced[:,1])
    plt.show()

def clusterGraph(method,graph,nodeID):
    if method not in clusteringMethods:
        print "ERROR:Not a method\nExiting"
        quit()
    attrib = []
    for i in range(len(graph["nodes"])):
        tempArr = []
        for k in graph["nodes"][i]["attr"]:
            tempArr.append(graph["nodes"][i]["attr"][k])
        attrib.append(tempArr)
    attrib = scale(np.array(attrib))
    estimator = clusteringMethods[method](attrib)
    cols = map(lambda x: plt.cm.Set3(np.linspace(0, 1, 6))[x] , estimator.labels_)
    plt.scatter(attrib[:,0],attrib[:,1],c=cols)
    plt.show()
    for i in range(len(estimator.labels_)):
        graph["nodes"][i]["attr"]["cluster"] = int(estimator.labels_[i])
        graph["nodes"][i]["col"] = ['red','green','blue'][int(estimator.labels_[i])]
    graph["nodes"][map(lambda x:x["id"],graph["nodes"]).index(nodeID)]["col"] = "yellow"
    return graph

def childifyGraph(graph,nodeID):
    newNodes = []
    newEdges = []
    newNodes.append(graph["nodes"].pop(map(lambda x:x["id"],graph["nodes"]).index(nodeID)))
    for c in np.unique(map(lambda x: x["attr"]["cluster"],graph["nodes"])):
        cname = "cluster"+str(c)
        tempObj = {"id": cname}
        tempObj["children"] = []
        for child in filter(lambda x: x["attr"]["cluster"]==0, graph["nodes"]):
            tempObj["children"].append(child)
        nodeSize = len(tempObj["children"])
        tempObj["size"] = nodeSize
        newNodes.append(tempObj)
        newEdges.append({"source":nodeID,"target":cname})
    return {"nodes":newNodes,"edges":newEdges}

def runExtraction(args):
    inFile = args.graph
    method = args.method
    outFile = args.out
    nodeID = int(args.id)

    origGraph = loadGraph(inFile)
    subGraph = queryGraph(origGraph,nodeID)
    clusteredGraph = clusterGraph(method,subGraph,nodeID)
    childGraph = childifyGraph(clusteredGraph,nodeID)
    o = open(outFile,"w")
    o.write(json.dumps(childGraph))

def loadGraph(inFile):
    return json.loads(open(inFile,"r").readline())

parser = argparse.ArgumentParser(description='Extractor and clustering on large graphs',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
subparsers = parser.add_subparsers(help="Task to perform")

parser_cluster = subparsers.add_parser('cluster', help='Extract nodes linked to an ID and cluster', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser_cluster.add_argument('method',help='Type of clustering to perform [kmeans|dbscan]')
parser_cluster.add_argument('id',help='Node id used to perform extraction')
parser_cluster.add_argument('graph',help='Graph in spesific JSON format')
parser_cluster.add_argument('out',help='Outfile name')
parser_cluster.set_defaults(func=runExtraction)

parser_cluster = subparsers.add_parser('pca', help='Extract nodes linked to an ID and cluster', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser_cluster.add_argument('id',help='Node id used to perform extraction')
parser_cluster.add_argument('graph',help='Graph in spesific JSON format')
parser_cluster.set_defaults(func=runPCA)

args = parser.parse_args()
args.func(args)
