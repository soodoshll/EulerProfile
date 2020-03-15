import threading
import time
import config

import paramiko
import os
import utils

import argparse

server_num = len(config.server_hosts)
server_ssh = [paramiko.SSHClient() for host in config.server_hosts]


for i in range(server_num):
  ssh = server_ssh[i]
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(config.server_hosts[i])

def stop_server(ssh):
  cmd = "rm %s/server* ; pkill -f -9 start_server.py ; pkill -f -9 sample_test.py"%(config.log_dir)
  stdin, stdout, stderr = ssh.exec_command(cmd)
  result = stdout.read()

def start_server(ssh, host_name, shard_ids, directory, thread):
  stop_server(ssh)
  time.sleep(5)
  script_path = os.path.join(config.experiment_dir, "start_server.py") 
  print "starting server", host_name
  for shard_id in shard_ids:
    # print "starting server", shard_id
    cmd = "bash -lc \"python %s --shard_idx %d --shard_num %d --directory %s --thread_num %d > %s 2> %s &\""%(
      script_path, shard_id, shard_num, directory, thread, 
      config.log_dir + "/server.out." + str(shard_id),
      config.log_dir + "/server.err." + str(shard_id)
    )
    # cmd = "ls"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    # result = stdout.read()

def wait_server(ssh, shard_ids):
  print "waiting..."
  for shard_id in shard_ids:
    result = ""
    while result.find("service start") < 0:
      cmd = "tail -n 1 %s/server.err.%d"%(config.log_dir, shard_id)
      stdin, stdout, stderr = ssh.exec_command(cmd)
      result = stdout.read()

def test(ssh, seed_num, fanout, steps, duration, partition, feats, node_ids):
  script_path = os.path.join(config.experiment_dir, "sample_test.py") 
  for i in range(args.clients_per_machine):
    cmd = "bash -lc \"python %s %d %d %d -d %f -i %d %s -p %s -m %d > %s 2> %s &\""%(
      script_path, seed_num, fanout, steps, duration, node_ids, 
      "-f " + str(feats) if feats else "", partition, len(config.worker_hosts), 
      config.log_dir + "/client.out." + str(i),
      config.log_dir + "/client.err." + str(i)
    )
    # print cmd
    # time.sleep(0.1)
    # cmd = "ls"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    # result = stdout.read()

def wait_client(ssh):
  results = []
  for i in range(args.clients_per_machine):
    result = ""
    while result.find("result") < 0:
      cmd = "tail -n 1 %s/client.out.%d"%(config.log_dir, i)
      stdin, stdout, stderr = ssh.exec_command(cmd)
      result = stdout.read()
      time.sleep(0.5)
    results.append(result)
  return results

def start_and_wait(server_id, partitions, directory, thread):
  try:
    start_server(server_ssh[server_id], config.server_hosts[server_id], partitions, directory, thread)
    wait_server(server_ssh[server_id], partitions)
  except paramiko.ssh_exception.ChannelException:
    print "retrying..."
    server_ssh[server_id] = paramiko.SSHClient()
    server_ssh[server_id].set_missing_host_key_policy(paramiko.AutoAddPolicy())
    server_ssh[server_id].connect(config.server_hosts[server_id])
    start_and_wait(server_id, partitions, directory, thread)

import sys 

parser = argparse.ArgumentParser()
parser.add_argument('command', type=str)
parser.add_argument('-p', '--partition', type=str, default="random")
parser.add_argument('-t', '--thread_num', type=int, default=48)

parser.add_argument('-s', '--seed_num', type=int, default=1000)
parser.add_argument('-F', '--fanout', type=int, default=10)
parser.add_argument('-S', '--steps', type=int, default=2)
parser.add_argument('-d', '--duration', type=float, default=20)
parser.add_argument('-f', '--feature', type=int, default=None)
parser.add_argument('-c', '--clients_per_machine', type=int, default=12)

args = parser.parse_args()

if args.command=='start':
  thread_num = args.thread_num
  partition = args.partition
  directory = config.partition_config[partition]['directory']
  partition_nodes_num = config.partition_config[partition]['partition']
  shard_num = len(partition_nodes_num)
  partition_num_per_machine = shard_num / server_num
  for server_id in range(server_num):
    print shard_num, server_num, partition_num_per_machine
    partitions = [server_id + i * server_num for i in range(partition_num_per_machine)]
    start_and_wait(server_id, partitions, directory, thread_num)
elif args.command=='stop':
  for i in server_ssh:
    stop_server(i)
elif args.command=='test':
  client_num = len(config.worker_hosts)
  client_ssh = [paramiko.SSHClient() for host in config.worker_hosts]
  for i in range(client_num):
    ssh = client_ssh[i]
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(config.server_hosts[i])
    stdin, stdout, stderr = ssh.exec_command("rm %s/client* ; pkill -f -9 sample_test.py"%(config.log_dir))
    result = stdout.read()
  client_thread = [threading.Thread(target=test, 
    args=(client_ssh[i], args.seed_num, args.fanout, args.steps, args.duration, args.partition,
          args.feature, i)) 
    for i in range(client_num)]
  for t in client_thread:
    t.start()
  
  time.sleep(2)
  print "waiting for results"
  result_all = []
  num_sampled_nodes = 0
  num_samples = 0
  dur_all = []
  tput_all = []
  for i in range(client_num):
    machine_name = config.worker_hosts[i]
    result = wait_client(client_ssh[i])
    result_tput = [float(x.strip().split(" ")[-1]) for x in result]
    result_time = [float(x.strip().split(" ")[-2]) for x in result]
    print machine_name, sum(result_time)/len(result_time), sum(result_tput)
    dur_all.append(sum(result_time)/len(result_time))
    tput_all.append(sum(result_tput))

  print "avg dur:", sum(dur_all)/len(dur_all), "ms"\
        " | tput:", sum(tput_all)
  for t in client_thread:
    t.join()