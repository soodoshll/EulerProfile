import tf_euler
import tensorflow as tf
import config
import time
import argparse
import numpy as np
import random 

parser = argparse.ArgumentParser()
parser.add_argument('seed_num', type=int)
parser.add_argument('fanout', type=int)
parser.add_argument('steps', type=int)
parser.add_argument('-d', '--duration', type=float)
parser.add_argument('-n', '--num', type=int)
parser.add_argument('-l', '--local', action='store_true')
parser.add_argument('-f', '--feature', type=int)
parser.add_argument('-i', '--id', type=int, default=0)
parser.add_argument('-p', '--partition', type=str, default="random")
parser.add_argument('-m', '--machine_num', type=int, default=1)

args = parser.parse_args()
# NUM_NODES = 232965
client_machine_num = args.machine_num
partition_nodes_num = config.partition_config[args.partition]['partition']

if not args.duration and not args.num:
  print "at least one of -d or -n need to be specified."
  exit()

if args.local:
  tf_euler.initialize_embedded_graph('reddit/48', graph_type='compact')
else:
  tf_euler.initialize_graph({'mode': 'Remote',
                           'zk_server': config.zk_addr,
                           'zk_path': config.zk_path})

def sample_and_flatten(input, fanout):
  sample = tf_euler.sample_neighbor(input, [0], fanout)
  return tf.reshape(sample[0], [-1])

def test_sample(seed_num, fanout, steps):
  layers = [tf_euler.sample_node(seed_num, 0)]

  for i in range(steps):
    layers.append(sample_and_flatten(layers[-1], fanout))

  # layers.append(sample_and_flatten(layers[-1], fanout))
  with tf.Session() as sess:
    start_t = time.time()
    output = sess.run(layers)
    for i in range(len(output)):
      print i, len(output[i])
    consumed_time = time.time() - start_t
    print "time: ", consumed_time

def get_seed(node_id, seed_num):
  ptr = 0
  data = []
  partition_num = len(partition_nodes_num)
  partition_per_machine = partition_num / client_machine_num
  local_partition = [node_id + i * client_machine_num for i in range(partition_per_machine)]
  for i in local_partition:
    num = partition_nodes_num[i]
    data += range(i, i + client_machine_num * num, client_machine_num)
  print len(data)
  random.shuffle(data)
  while True:
    if ptr + seed_num >= len(data):
      ptr = 0
      # random.shuffle(data)
    yield data[ptr : ptr + seed_num]
    ptr += seed_num

def test_sample_multihop(seed_num, fanout, steps, duration, node_id):
  seed_ph = tf.placeholder(tf.int64, shape=[seed_num])
  samples = [seed_ph]
  samples_uniqued = [tf.unique(seed_ph)[0]]
  for i in range(steps):
    seed = tf.unique(samples_uniqued[-1])[0]
    sample = sample_and_flatten(seed, fanout)
    samples.append(sample)
    sample_unique = tf.unique(sample)[0]
    samples_uniqued.append(sample_unique)
  if args.feature:
    feats = tf_euler.get_dense_feature(sample_unique, [0], [args.feature])
  sample_num = 0
  seed_generator = get_seed(node_id, seed_num)
  first_batch = seed_generator.next()
  with tf.Session() as sess:
    start_t = time.time()
    edges_tot = 0
    consumed_time = 0
    total_nodes = 0
    sample_time = 0
    while (args.duration and time.time() - start_t < duration) or \
          (args.num and sample_num < args.num):
      # print sample_num
      t0 = time.time()
      seed = seed_generator.next()
      sample_time += time.time() - t0
      start_t0 = time.time()
      if args.feature:
        output = sess.run([samples, feats], feed_dict={seed_ph : seed})
        # print output
      else:
        output = sess.run([samples], feed_dict={seed_ph : seed})
      edges_tot += sum(len(x) for x in output[0][1:])
      # print ' '
      # total_nodes += sum([len(x) for x in output[0]])
      consumed_time += time.time() - start_t0
      # print(len(output[0][-1]))
      # edges_tot += sum([len(x) for x in output[0][1:]])
      # first_layer = output[0][1]
      # s = set()
      # for x in first_layer:
        # s.add(x)
      # print len(s)
      sample_num += 1
    # consumed_time = time.time() - start_t
    # print "result:", consumed_time, sample_num, (total_nodes), consumed_time / sample_num
    print "sample seed time:", sample_time
    print "result:", consumed_time / sample_num, edges_tot / consumed_time / 1000

test_sample_multihop(args.seed_num, args.fanout, args.steps, args.duration, args.id)