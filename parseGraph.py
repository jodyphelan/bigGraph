#! /usr/bin/python
from sys import argv
import json
from tqdm import tqdm

script,metaFile,inFile,outFile = argv

def file_len(fname):
    with open(fname) as f:
        for i,l in enumerate(f):
            pass
    return i+1

def generateNode(i):
    tempObj = {}
    tempArr = meta[i].split("\t")
    for j,attr in enumerate(header):
        tempObj[attr] = tempArr[j]
    return {'id':i, "attr":tempObj}


m = open(metaFile,"r")
meta = []
header = m.readline().rstrip().split("\t")
for i in tqdm(range(file_len(metaFile)-1)):
    l = m.readline()
    meta.append(l.rstrip())

nodes = []
edges = []
f = open(inFile,"r")
for line in tqdm(f.readlines()):
    if (line[0]=="%"):
        continue
    source,target = line.rstrip().split(" ")
    source = int(source)
    target = int(target)
    if source not in map(lambda x:x["id"],nodes):
        tempObj = generateNode(source)
        nodes.append(tempObj)
    if target not in map(lambda x:x["id"],nodes):
        tempObj = generateNode(target)
        nodes.append(tempObj)
    edges.append({"source":source,"target":target})

graph = {"nodes":nodes,"edges":edges}
o = open(outFile,"w")
o.write(json.dumps(graph))
