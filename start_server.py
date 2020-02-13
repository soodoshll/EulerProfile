import euler
import argparse
import config

parser = argparse.ArgumentParser()
parser.add_argument('--shard_idx', type=int)
args = parser.parse_args()

euler.start_and_wait(directory = config.directory, # graph data directory
                     loader_type = "Remote",
                     hdfs_addr = config.hdfs_addr,
                     shard_idx = args.shard_idx, # shard idx
                     shard_num = config.shard_num, # shard number
                     zk_addr = config.zk_addr, # Zookeeper address, ip:port
                     zk_path = config.zk_path, # Zookeeper path
                     graph_type = config.graph_type, # graph type, compact / fast, the default is compact.
                     server_thread_num = config.server_thread_num # euler service thread number, the default is 4.
)