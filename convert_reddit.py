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
import scipy.sparse as sp

from networkx.readwrite import json_graph
from euler.tools import json2dat

version_info = list(map(int, nx.__version__.split('.')))
major = version_info[0]
minor = version_info[1]
assert (major <= 1) and (minor <=
                         11), "networkx major version > 1.11, should be 1.11"



def load_data(prefix, normalize=True, load_walks=False):
  coo_adj = sp.load_npz(prefix + '_self_loop_graph.npz')
  G = nx.from_scipy_sparse_matrix(coo_adj)
  reddit_data = np.load(prefix + '_data.npz')
  feats = reddit_data['feature']

  id_map = list(map(int, reddit_data['node_ids']))
  class_map = list(map(int, reddit_data['label']))
  node_types = list(map(int, reddit_data['node_types']))

  ## Make sure the graph has edge train_removed annotations
  ## (some datasets might already have this..)
  print("Loaded data.. now preprocessing..")
  return G, feats, id_map, class_map, node_types

def node_type_id(node_types, node_id):
  return node_types[node_id] - 1

def onehot(x, n):
  return [0.]*x + [1.] + [0.]*(n - x - 1)

def convert_data(prefix, dest_prefix, partition_num = 1):
  with_weight = False
  G, feats, id_map, class_map, node_types = load_data(prefix)

  meta = {
      "node_type_num": 3,
      "edge_type_num": 1,
      "node_uint64_feature_num": 0,
      "node_float_feature_num": 2,  # 0 for class 1 for features
      "node_binary_feature_num": 0,
      "edge_uint64_feature_num": 0,
      "edge_float_feature_num": 0,
      "edge_binary_feature_num": 0
  }

  meta_out = open(dest_prefix + '_meta.json', 'w')
  meta_out.write(json.dumps(meta))
  meta_out.close()

  # ==== Parition ====
  # Random
  partition_dict = {}
  partition_nodes = [[] for i in range(partition_num)]
  new_id = {}
  for node in G.nodes():
    partition_id = random.randint(0, partition_num - 1)
    partition_dict[node] = partition_id
    new_id[node] = len(partition_nodes[partition_id]) * partition_num + partition_id
    
    partition_nodes[partition_id].append(node)
  print([len(x) for x in partition_nodes])
  out_files = [open(dest_prefix + '_data_%d.json'%(i), 'w') for i in range(partition_num)]

  # out_val = open(prefix + '_val.id', 'w')
  # out_train = open(prefix + '_train.id', 'w')
  # out_test = open(prefix + '_test.id', 'w')
  # out_vec = [out_train, out_val, out_test]
  out = open(prefix + '_data.json', 'w')
  cnt = 0
  z = 0
  for node in G.nodes():
    cnt += 1
    if (cnt % 1000 == 0):
      print(cnt)
    this_node = G[node]
    buf = {}
    buf["node_id"] = new_id[node]
    buf["node_type"] = node_type_id(node_types, node)
    # out_vec[node_type_id(G.node[node])].write(str(id_map[node]) + '\n')
    buf["node_weight"] = len(this_node) if with_weight else 1
    buf["neighbor"] = {}
    for i in range(0, meta["edge_type_num"]):
      buf["neighbor"][str(i)] = {}
    for n in this_node:
      id_n = new_id[n]
      buf["neighbor"]['0'][str(id_n)] = 1
    buf["uint64_feature"] = {}
    buf["float_feature"] = {}
    buf["float_feature"][0] = onehot(class_map[node], 41)
    buf["float_feature"][1] = list(feats[id_map[node]])
    buf["binary_feature"] = {}
    buf["edge"] = []
    # if (len(this_node) == 0) :
      # print("ZERO EDGE")
      # z += 1
    for tar in this_node:
      ebuf = {}
      ebuf["src_id"] = new_id[node]
      ebuf["dst_id"] = new_id[tar]
      # print("edge ", new_id[node], new_id[tar])
      ebuf["edge_type"] = 0
      ebuf["weight"] = 1
      ebuf["uint64_feature"] = {}
      ebuf["float_feature"] = {}
      ebuf["binary_feature"] = {}
      buf["edge"].append(ebuf)
    out_files[partition_dict[node]].write(json.dumps(buf) + '\n')
  # print(cnt, z)
  for i in out_files:
    i.close()

if __name__ == '__main__':
  #print('download ppi data..')
  #url = 'http://snap.stanford.edu/graphsage/ppi.zip'
  #urllib.urlretrieve(url, 'ppi.zip')
  #with zipfile.ZipFile('ppi.zip') as ppi_zip:
  #  print('unzip data..')
  #  ppi_zip.extractall()

  prefix = 'reddit/reddit'
  dest_prefix = "reddit/12/reddit_12"
  partition_num = 12
  convert_data(prefix, dest_prefix, partition_num)
  for i in range(partition_num):
    print ("converting:", i)
    c = json2dat.Converter(dest_prefix + '_meta.json', dest_prefix + '_data_%d.json'%i,
                    dest_prefix + '_data_%d.dat'%i)
    c.do()
  # c = json2dat.Converter(prefix + '_meta.json', prefix + '_data.json',
  #                        prefix + '_data.dat')
  # c.do()
## ffsd QQQ
