# Copyright 2018 Alibaba Group Holding Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

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

def load_data(prefix, load_walks=False):
  coo_adj = sp.load_npz(prefix + 'reddit_self_loop_graph.npz')
  G = nx.from_scipy_sparse_matrix(coo_adj)
  for i in G.nodes():
      print(i)
  return G

if __name__ == '__main__':
  prefix = 'reddit/'
  dest_prefix = 'reddit/metis'
  partition_num = 8
  G = load_data(prefix)
#   result = nxmetis.partition(G, partition_num)
#   print(result)
#   for i in range(partition_num):
    # print ("converting:", i)
    # c = json2dat.Converter(dest_prefix + '_meta.json', dest_prefix + '_data_%d.json'%i,
                    # dest_prefix + '_data_%d.dat'%i)
    # c.do()