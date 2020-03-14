hdfs_addr = "hdfs://node1:9000/"
zk_addr = "node1:2181"
zk_path = "/euler"
graph_type = "fast"
# server_thread_num = 12


server_hosts = ["node1", "node2", "node3", "node4"]
worker_hosts = ["node1", "node2", "node3", "node4"]

# server_hosts = ["node1"]
# worker_hosts = ["node1"]

experiment_dir = "/home/ubuntu/profile/"

log_dir = "/home/ubuntu/profile/log/"
# server_script_path = ""

partition_nodes_num_random = [4804, 4885, 4832, 4797, 4885, 4923, 4720, 
4907, 4754, 4906, 4888, 4863, 4657, 4933, 4843, 4878, 4910, 4836, 4862, 
4945, 4933, 4842, 4870, 4833, 5002, 4828, 4817, 4876, 4753, 4902, 4882, 
4718, 4879, 4853, 4877, 4736, 4823, 4828, 4726, 4798, 4922, 4892, 4874, 
4834, 4907, 4940, 4852, 4940]

partition_nodes_num_metis = [4730, 4999, 4711, 4972, 4730, 4999, 4711, 
4972, 4730, 4999, 4711, 4972, 4730, 4999, 4711, 4972, 4730, 4999, 4711,
4972, 4730, 4999, 4711, 4972, 4730, 4999, 4711, 4972, 4730, 4999, 4711, 
4972, 4730, 4999, 4711, 4972, 4730, 4999, 4711, 4972, 4730, 4999, 4711, 
4972, 4732, 5002, 4721, 4978]

def partition_refine(partition, num):
  return [sum(partition[i:i+num]) for i in range(0, 48, num)]

# directory = "/data/reddit-metis/"
# partition_nodes_num = partition_refine(partition_nodes_num_metis, 1)

# directory = "/data/reddit48/"
# partition_nodes_num = partition_refine(partition_nodes_num_random, 1)

partition_config = {}

partition_config['local'] = {
  "directory" : "/data/reddit48/",
  "partition" : partition_refine(partition_nodes_num_random, 4)}

partition_config['random'] = {
  "directory" : "/data/reddit48/",
  "partition" : partition_nodes_num_random}

partition_config['metis'] = {
  "directory" : "/data/reddit-metis/",
  "partition" : partition_nodes_num_metis}