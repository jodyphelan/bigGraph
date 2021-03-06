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


def plotPCA(attrib,cols):
    pca = pcaCluster(attrib)
    pca.n_components = 2
    attrib_reduced = pca.fit_transform(attrib)
    plt.scatter(attrib_reduced[:,0],attrib_reduced[:,1],c=cols)
    plt.show()


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
    cols = ["black" for x in range(len(attrib))]
    plotPCA(attrib,cols)

def discretiseGraph(args):
    graph = loadGraph(args.graph)
    attr = map(lambda x:x,graph["nodes"][0]["attr"])
    for a in attr:
        vals = []
        try:
            vals = np.unique(map(lambda x: int(x["attr"][a]),graph["nodes"]))
            print "OK!"
        except:
            uniqueVals = list(set(map(lambda x: x["attr"][a],graph["nodes"])))
            print uniqueVals
            numericalVals =  list(range(0,len(uniqueVals)))
            vals = map(lambda x: numericalVals[uniqueVals.index(x["attr"][a])], graph["nodes"])
            print "Discretised!"
        for i,val in enumerate(vals):
            graph["nodes"][i]["attr"][a] = val
    o = open(args.out,"w")
    o.write(json.dumps(graph))

def clusterGraph(method,graph,nodeID,plot):
    clusteringMethods = {"kmeans":kmeansCluster,"dbscan":dbscanCluster}
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
    if (plot==True):
        cols = map(lambda x: plt.cm.Set3(np.linspace(0, 1, 6))[x] , estimator.labels_)
        plotPCA(attrib,cols)
    for i in range(len(estimator.labels_)):
        graph["nodes"][i]["attr"]["cluster"] = int(estimator.labels_[i])
        graph["nodes"][i]["col"] = ['red','green','blue',"purple","pink","violet"][int(estimator.labels_[i])]
    graph["nodes"][map(lambda x:x["id"],graph["nodes"]).index(nodeID)]["col"] = "yellow"
    return graph

def extractFeatures(graph,config):
    newNodes = []
    newEdges = graph["edges"]
    for node in graph["nodes"]:
        tempObj = {"id":node["id"],"attr":{}}
        for attr in config:
            tempObj["attr"][attr] = node["attr"][attr]

        newNodes.append(tempObj)
    return {"nodes":newNodes,"edges":newEdges}

def fextract(args):
    inFile = args.graph
    config = map(lambda x: x.rstrip(), open(args.config,"r").readlines())
    print config
    origGraph = loadGraph(inFile)
    extractedGraph = extractFeatures(origGraph,config)
    o = open(args.out,"w")
    o.write(json.dumps(extractedGraph))

def childifyGraph(graph,nodeID):
    newNodes = []
    newEdges = []
    newNodes.append(graph["nodes"].pop(map(lambda x:x["id"],graph["nodes"]).index(nodeID)))
    for c in np.unique(map(lambda x: x["attr"]["cluster"],graph["nodes"])):
        cname = "cluster"+str(c)
        print "Collapsing " + cname
        tempObj = {"id": cname}
        tempObj["children"] = []
        for child in filter(lambda x: x["attr"]["cluster"]==c, graph["nodes"]):
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
    plot = args.plot

    origGraph = loadGraph(inFile)
    subGraph = queryGraph(origGraph,nodeID)
    clusteredGraph = clusterGraph(method,subGraph,nodeID,plot)
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
parser_cluster.add_argument('--plot', default=False, const=True, action = 'store_const', help='Plot clustering of samples using pca')
parser_cluster.set_defaults(func=runExtraction)

parser_pca = subparsers.add_parser('pca', help='Extract nodes linked to an ID and cluster', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser_pca.add_argument('id',help='Node id used to perform extraction')
parser_pca.add_argument('graph',help='Graph in spesific JSON format')
parser_pca.set_defaults(func=runPCA)

parser_fextract = subparsers.add_parser('fextract', help='Extract nodes linked to an ID and cluster', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser_fextract.add_argument('graph',help='Graph in spesific JSON format')
parser_fextract.add_argument('config',help='ConfigFile')
parser_fextract.add_argument('out',help='OutFile')
parser_fextract.set_defaults(func=fextract)

parser_disc = subparsers.add_parser('discretise', help='Extract nodes linked to an ID and cluster', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser_disc.add_argument('graph',help='Graph in spesific JSON format')
parser_disc.add_argument('out',help='OutFile')
parser_disc.set_defaults(func=discretiseGraph)

args = parser.parse_args()
args.func(args)
