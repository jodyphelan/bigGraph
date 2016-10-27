from sys import argv
import json

script,metaFile,inFile,outFile = argv

def generateNode(i):
    tempObj = {}
    for k in meta[i]:
        tempObj[k] = float(meta[i][k])
    return {'id':i, "attr":tempObj}


m = open(metaFile,"r")
meta = []
header = m.readline().rstrip().split("\t")
for l in m.readlines():
    tempArr = l.rstrip().split("\t")
    tempObj = {}
    for i in range(len(tempArr)):
        tempObj[header[i]] = tempArr[i]
    meta.append(tempObj)

nodes = []
edges = []
f = open(inFile,"r")
for line in f.readlines():
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
