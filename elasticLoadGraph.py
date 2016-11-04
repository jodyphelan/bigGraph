#! /usr/bin/python
from sys import argv
import json
from tqdm import tqdm
from elasticsearch import Elasticsearch
es = Elasticsearch()

def loadNode(i,node):
    doc = json.dumps(node)
    res = es.index(index="tb", doc_type='nodes', id=i, body=doc)

def loadEdge(i,obj):
    doc = json.dumps(obj)
    res = es.index(index="tb", doc_type='edges', id=i, body=doc)


graph = json.loads(open(argv[1]).readline())
nodeIDX = {}
for i,node in enumerate(tqdm(graph["nodes"])):
    nodeIDX[node["id"]] = i
    loadNode(i,node)

for i,edge in enumerate(tqdm(graph["edges"])):
    obj = {"source":nodeIDX[edge["source"]],"target":nodeIDX[edge["target"]]}
    loadEdge(i,obj)
