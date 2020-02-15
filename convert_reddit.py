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

import multiprocessing
from multiprocessing import Process, Queue

from networkx.readwrite import json_graph
from euler.tools import json2dat

version_info = list(map(int, nx.__version__.split('.')))
major = version_info[0]
minor = version_info[1]
assert (major <= 1) and (minor <=
                         11), "networkx major version > 1.11, should be 1.11"


def load_data(prefix, normalize=True, load_walks=False):
  G_data = json.load(open(prefix + "-G.json"))
  G = json_graph.node_link_graph(G_data)
  if isinstance(G.nodes()[0], int):
    conversion = lambda n: int(n)
  else:
    conversion = lambda n: n

  if os.path.exists(prefix + "-feats.npy"):
    feats = np.load(prefix + "-feats.npy")
  else:
    print("No features present.. Only identity features will be used.")
    feats = None
  id_map = json.load(open(prefix + "-id_map.json"))
  id_map = {conversion(k): int(v) for k, v in id_map.items()}
  i = 1
  walks = []
  class_map = json.load(open(prefix + "-class_map.json"))
  if isinstance(list(class_map.values())[0], list):
    lab_conversion = lambda n: n
  else:
    lab_conversion = lambda n: int(n)

  class_map = {conversion(k): lab_conversion(v) for k, v in class_map.items()}

  ## Remove all nodes that do not have val/test annotations
  ## (necessary because of networkx weirdness with the Reddit data)
  broken_count = 0
  for node in G.nodes():
    if not 'val' in G.node[node] or not 'test' in G.node[node]:
      G.remove_node(node)
      broken_count += 1
  print(
      "Removed {:d} nodes that lacked proper annotations due to networkx versioning issues"
      .format(broken_count))

  ## Make sure the graph has edge train_removed annotations
  ## (some datasets might already have this..)
  print("Loaded data.. now preprocessing..")
  for edge in G.edges():
    if (G.node[edge[0]]['val'] or G.node[edge[1]]['val']
        or G.node[edge[0]]['test'] or G.node[edge[1]]['test']):
      G[edge[0]][edge[1]]['train_removed'] = True
    else:
      G[edge[0]][edge[1]]['train_removed'] = False

  if normalize and not feats is None:
    from sklearn.preprocessing import StandardScaler
    train_ids = np.array([
        id_map[n] for n in G.nodes()
        if not G.node[n]['val'] and not G.node[n]['test']
    ])
    train_feats = feats[train_ids]
    scaler = StandardScaler()
    scaler.fit(train_feats)
    feats = scaler.transform(feats)

  if load_walks:
    with open(prefix + "-walks.txt") as fp:
      for line in fp:
        walks.append(map(conversion, line.split()))

  return G, feats, id_map, walks, class_map


def node_type_id(dic):
  if dic['val']:
    return 1
  elif dic['test']:
    return 2
  else:
    return 0


def edge_type_id(dic):
  if dic['train_removed']:
    return 1
  else:
    return 0


def convert_data(prefix, dest_prefix, partition_num = 1):
  with_weight = False
  G, feats, id_map, walks, class_map = load_data(prefix)
  max_edge_type = 0

  meta = {
      "node_type_num": 3,
      "edge_type_num": 2,
      "node_uint64_feature_num": 0,
      "node_float_feature_num": 0,  # 0 for class 1 for features
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
  nodes_num = len(G.nodes())
  parallel_num = 16
  # out_val = open(prefix + '_val.id', 'w')
  # out_train = open(prefix + '_train.id', 'w')
  # out_test = open(prefix + '_test.id', 'w')
  # out_vec = [out_train, out_val, out_test]
  q = Queue(65536)
  def convert_process(q, pid):
    for node_id in range(pid, nodes_num, parallel_num):
      node = G.nodes()[node_id]
      this_node = G[node]
      buf = {}
      buf["node_id"] = new_id[node]
      buf["node_type"] = node_type_id(G.node[node])
      # out_vec[node_type_id(G.node[node])].write(str(id_map[node]) + '\n')
      buf["node_weight"] = len(this_node) if with_weight else 1
      buf["neighbor"] = {}
      for i in range(0, meta["edge_type_num"]):
        buf["neighbor"][str(i)] = {}
      for n in this_node:
        id_n = new_id[node]
        buf["neighbor"][str(edge_type_id(this_node[n]))][id_n] = 1
      buf["uint64_feature"] = {}
      # buf["float_feature"] = {}
      # buf["float_feature"][0] = [class_map[node]]
      # buf["float_feature"][1] = list(feats[id_map[node]])
      buf["binary_feature"] = {}
      buf["edge"] = []
      for tar in this_node:
        ebuf = {}
        ebuf["src_id"] = new_id[node]
        ebuf["dst_id"] = new_id[tar]
        ebuf["edge_type"] = edge_type_id(this_node[tar])
        # max_edge_type = max(max_edge_type, ebuf["edge_type"])
        ebuf["weight"] = 1
        ebuf["uint64_feature"] = {}
        ebuf["float_feature"] = {}
        ebuf["binary_feature"] = {}
        buf["edge"].append(ebuf)
      q.put([partition_dict[node], json.dumps(buf) + '\n'])
  
  pool = [Process(target=convert_process, args=(q, i)) for i in range(parallel_num)]
  for i in pool:
    i.start()
  cnt = 0
  while (cnt < nodes_num):
    cur = q.get()
    out_files[cur[0]].write(cur[1])
    cnt += 1
    if (cnt % 1000 == 0):
      print(cnt)
  for i in pool:
    i.join()
  for i in out_files:
    i.close()
  # for i in out_vec:
    # i.close()


if __name__ == '__main__':
  #print('download ppi data..')
  #url = 'http://snap.stanford.edu/graphsage/ppi.zip'
  #urllib.urlretrieve(url, 'ppi.zip')
  #with zipfile.ZipFile('ppi.zip') as ppi_zip:
  #  print('unzip data..')
  #  ppi_zip.extractall()

  prefix = 'reddit/reddit'
  dest_prefix = 'reddit/random_tmp/reddit_random'
  partition_num = 8
  convert_data(prefix, dest_prefix, partition_num)
  for i in range(partition_num):
    print ("converting:", i)
    c = json2dat.Converter(dest_prefix + '_meta.json', dest_prefix + '_data_%d.json'%i,
                    dest_prefix + '_data_%d.dat'%i)
    c.do()
  # c = json2dat.Converter(prefix + '_meta.json', prefix + '_data.json',
  #                       prefix + '_data.dat')
  # c.do()
## ffsd QQQ

# 8min37s