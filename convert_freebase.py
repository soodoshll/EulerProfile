from KGDataset import *
dataset  = KGDatasetFreebase(".", name="freebase", read_triple="false")

import time
# First try to read val set

t0 = time.time()
src, rel, dest = dataset.read_triple(os.path.join(dataset.path, 'valid.txt'), "valid")
print("reading data: ", time.time() - t0, "s")

node_num = 86054151
partition_num = 8 * 12
# partition_num = 1

# # Random partition
partition_nodes = [[] for i in range(partition_num)]
partition_map = []

import random

t0 = time.time()
for i in range(node_num):
  p_id = random.randint(0, partition_num - 1)
  # p_id = 0
  partition_map.append(p_id)
  partition_nodes[p_id].append(i)

# Backup
import pickle
pickle.dump(partition_nodes, open("./freebase/freebase_random_96.pkl", "wb"))

# Renunmber the id
import numpy as np
id_map = np.zeros(node_num)
for p_id in range(partition_num):
  partition = partition_nodes[p_id]
  for i in range(len(partition)):
    old_id = partition[i]
    new_id = p_id + i * partition_num
    id_map[old_id] = new_id
for i in range(node_num):
  id_map[i] = i
print("partition:", time.time() - t0, "s")

# Build adj_list
t0 = time.time()
adj_list = [[] for i in range(node_num)]
for i in range(len(src)):
  s, r, d = src[i], rel[i], dest[i]
  adj_list[s].append((d,r))
print("Build adj_list:", time.time() - t0, "s")

# Save meta info
import json
dest_prefix = "./freebase/random/free_base"
meta = {
    "node_type_num": 1,
    # "edge_type_num": 14824,
    "edge_type_num": 1,
    "node_uint64_feature_num": 0,
    "node_float_feature_num": 1,
    "node_binary_feature_num": 0,
    "edge_uint64_feature_num": 0,
    "edge_float_feature_num": 0,
    "edge_binary_feature_num": 0
}
meta_out = open(dest_prefix + '_meta.json', 'w')
meta_out.write(json.dumps(meta))

# Open json files
import random
feature_dim = 100
feature_num = 100
# Generate some features
feature_pool = [list(np.random.random([feature_dim])) for i in range(feature_num)]
out_files = [open("%s_%d.json"%(dest_prefix, i), "w") for i in range(partition_num)]
out_buff = [[] for i in range(partition_num)]

t1 = time.time()
empty_dict = {}
for node in range(node_num):
  if node % 1000 == 0:
    t0 = time.time()
    for i in range(partition_num):
      out_files[i].write("\n".join(out_buff[i]))
    out_buff = [[] for i in range(partition_num)]
    print(node, time.time() - t1, "s", " | write to file: ", time.time() - t0, "s")
    t1 = time.time()

  buf = {}
  buf["node_id"] = id_map[node]
  # buf["node_id"] = node

  buf["node_type"] = 0
  buf["node_weight"] = 1
  buf["neighbor"] = {}
  for i in range(0, meta["edge_type_num"]):
    buf["neighbor"][str(i)] = {}
  for dest, edge_type in adj_list[node]:
    # dest_id = dest
    dest_id = id_map[dest]
    # edge_dict = buf["neighbor"][str(edge_type)]
    # if edge_dict is empty_dict:
    #   edge_dict = {}
    #   buf["neighbor"][str(edge_type)] = edge_dict
    # edge_dict[str(dest_id)] = 1
    buf["neighbor"]['0'][str(dest_id)] = 1

  buf["uint64_feature"] = {}
  buf["float_feature"] = {}
  buf["float_feature"][0] = random.choice(feature_pool)
  buf["binary_feature"] = {}
  buf["edge"] = []
  for dest, edge_type in adj_list[node]:
    ebuf = {}
    ebuf["src_id"] = id_map[node]
    ebuf["dst_id"] = id_map[dest]
    # ebuf["src_id"] = node
    # ebuf["dst_id"] = int(dest)
    # ebuf["edge_type"] = int(edge_type)
    ebuf["edge_type"] = 0
    ebuf["weight"] = 1
    ebuf["uint64_feature"] = {}
    ebuf["float_feature"] = {}
    ebuf["binary_feature"] = {}
    buf["edge"].append(ebuf)

  out_buff[partition_map[node]].append(json.dumps(buf))

for i in out_files:
  i.close()