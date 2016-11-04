#! /usr/bin/python
import json
import sys

nodes = []
edges = []
f = open(sys.argv[1])
f.readline()
nodeSet = set()
for l in (f.readlines()):
    from_gene_locus,from_symbol,from_product,to_gene_locus,to_symbol,to_product,count_links,cvg_over_mean,max_pos,type,subtype,dist2stt,fc_control,zscore,by_operon = l.split("\t")
    if from_gene_locus not in nodeSet:
        nodes.append({"id":from_gene_locus})
        nodeSet.add(from_gene_locus)
    if to_gene_locus not in nodeSet:
        nodes.append({"id":to_gene_locus})
        nodeSet.add(to_gene_locus)
    edges.append({"source":from_gene_locus,"target":to_gene_locus})

o = open(sys.argv[2],"w")
o.write(json.dumps({"nodes":nodes,"edges":edges}))
