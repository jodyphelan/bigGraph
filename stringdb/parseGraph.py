#! /usr/bin/python

import json
import sys

nodes = []
edges = []
f = open(sys.argv[1])
f.readline()
nodeSet = set()
for l in (f.readlines()):
    from_gene_locus,to_gene_locus,score = l.split(" ")
    from_gene_locus = from_gene_locus[6:]
    to_gene_locus = to_gene_locus[6:]
    if from_gene_locus not in nodeSet:
        nodes.append({"id":from_gene_locus})
        nodeSet.add(from_gene_locus)
    if to_gene_locus not in nodeSet:
        nodes.append({"id":to_gene_locus})
        nodeSet.add(to_gene_locus)
    if int(score)>int(sys.argv[2]):
        edges.append({"source":from_gene_locus,"target":to_gene_locus})

o = open(sys.argv[3],"w")
o.write(json.dumps({"nodes":nodes,"edges":edges}))
