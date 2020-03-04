# Using python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os
import random
import sys
import subprocess
import urllib
import zipfile

import networkx as nx
import numpy as np
import nxmetis

from networkx.readwrite import json_graph
import scipy.sparse as sp
import pickle
def load_data(prefix, load_walks=False):
  coo_adj = sp.load_npz(prefix + 'reddit_self_loop_graph.npz')
  G = nx.from_scipy_sparse_matrix(coo_adj)
  return G

if __name__ == '__main__':
  prefix = 'reddit/'
  output_file = 'reddit-metis-4.pkl'
  partition_num = 4
  # with open(output_file, "wb") as f:
  #   G = load_data(prefix)
  #   result = nxmetis.partition(G, partition_num)
  #   pickle.dump(result, f, protocol=2)
  
  refine_file = 'reddit-metis-4-12.pkl'
  refine_num = 12
  with open(output_file, "rb") as f:
    partition = pickle.load(f)[1]
  print(len(partition[0]))
  refine_per_part = [len(x)//refine_num for x in partition]
  refine = []
  for part in partition:
    random.shuffle(part)
  for i in range(refine_num):
    for j in range(partition_num):
      n = refine_per_part[j]
      if i == refine_num - 1:
        refine.append(partition[j][i*n : ])
      else:
        refine.append(partition[j][i*n : (i+1)*n])
  print ([len(x) for x in partition])
  print ([len(x) for x in refine])
  with open(refine_file, "wb") as f:
    pickle.dump(refine, f, protocol=2)
#   print(result)
#   for i in range(partition_num):
    # print ("converting:", i)
    # c = json2dat.Converter(dest_prefix + '_meta.json', dest_prefix + '_data_%d.json'%i,
                    # dest_prefix + '_data_%d.dat'%i)
    # c.do()