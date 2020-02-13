import euler
import argparse
import config

parser = argparse.ArgumentParser()
# parser.add_argument('--dir', type=str)
# parser.add_argument('--loader', type=str)
# parser.add_argument('--hdfs_addr', type=str)
# parser.add_argument('--hdfs_port', type=int)
# parser.add_argument('--shard_idx', type=int)
# parser.add_argument('--shard_num', type=int)
# parser.add_argument('--zk_addr', type=str)
# parser.add_argument('--zk_path', type=str)
# parser.add_argument('--sampler_type', type=str, default="node")
# parser.add_argument('--graph_type', type=str, default="compact")


args = parser.parse_args()

print args.integer


euler.start_and_wait(directory, # graph data directory
                     loader_type, # loader type
                     hdfs_addr, # HDFS address
                     hdfs_port, # HDFS port
                     shard_idx, # shard idx
                     shard_num, # shard number
                     zk_addr, # Zookeeper address, ip:port
                     zk_path, # Zookeeper path
                     global_sampler_type, # global_sampler_type: all / node / edge / none, the default is node.
                     graph_type, # graph type, compact / fast, the default is compact.
                     server_thread_num # euler service thread number, the default is 4.
)