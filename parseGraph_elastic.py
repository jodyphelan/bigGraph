#! /usr/bin/python
from sys import argv
import json
from tqdm import tqdm
from elasticsearch import Elasticsearch
es = Elasticsearch()


script,metaFile,inFile,outFile = argv

def file_len(fname):
    with open(fname) as f:
        for i,l in enumerate(f):
            pass
    return i+1

def loadNode(i):
    tempObj = {}
    tempArr = meta[i].split("\t")
    for j,attr in enumerate(header):
        tempObj[attr] = tempArr[j]
    doc = json.dumps({'id':i, "attr":tempArr})
    nodeIDX[i] = i
    res = es.index(index="graph", doc_type='nodes', id=i, body=doc)

def loadEdge(i,obj):
    i = str(i)
    doc = json.dumps(obj)
    res = es.index(index="graph", doc_type='edges', id=i, body=doc)


m = open(metaFile,"r")
print "Loading Meta data"
meta = []
header = m.readline().rstrip().split("\t")
for i in tqdm(range(file_len(metaFile)-1)):
    l = m.readline()
    meta.append(l.rstrip())


print "Pushing to elasticsearch"
nodes = set()
edges = set()
nodeIDX = {}
f = open(inFile,"r")
edgeIndex = 0
for i in tqdm(range(file_len(inFile))):
    line = f.readline()
    if (line[0]=="%"):
        continue
    source,target = line.rstrip().split(" ")
    source = int(source)
    target = int(target)
    if source not in nodes:
        loadNode(source)
    if target not in nodes:
        loadNode(target)
    loadEdge(edgeIndex,{"source":nodeIDX[source],"target":nodeIDX[target]})
    edgeIndex = edgeIndex+1
