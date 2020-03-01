hdfs_addr = "hdfs://node1:9000/"
zk_addr = "node1:2181"
zk_path = "/euler"
graph_type = "fast"
server_thread_num = 48

directory = "/data/reddit48/"

server_hosts = ["node1", "node2", "node3", "node4"]
worker_hosts = ["node1", "node2", "node3", "node4"]

experiment_dir = "/home/ubuntu/profile/"

log_dir = "/home/ubuntu/profile/log/"
# server_script_path = ""

partition_nodes_num_random = [4804, 4885, 4832, 4797, 4885, 4923, 4720, 
4907, 4754, 4906, 4888, 4863, 4657, 4933, 4843, 4878, 4910, 4836, 4862, 
4945, 4933, 4842, 4870, 4833, 5002, 4828, 4817, 4876, 4753, 4902, 4882, 
4718, 4879, 4853, 4877, 4736, 4823, 4828, 4726, 4798, 4922, 4892, 4874, 
4834, 4907, 4940, 4852, 4940]

partition_nodes_num_whole = [sum(partition_nodes_num_random)]

partition_nodes_num = partition_nodes_num_random