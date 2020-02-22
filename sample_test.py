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
parser.add_argument('duration', type=float)
parser.add_argument('-l', '--local', action='store_true')
args = parser.parse_args()

if args.local:
  tf_euler.initialize_embedded_graph('reddit/48', graph_type='fast')
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

NUM_NODES = 232965

def get_seed(node_num, seed_num):
  ptr = 0
  data = range(0, node_num)
  random.shuffle(data)
  while True:
    if ptr + seed_num >= node_num:
      ptr = 0
      print "set zero"
      random.shuffle(data)
    yield data[ptr : ptr + seed_num]
    ptr += seed_num
    # yield data[:seed_num]

def test_sample_multihop(seed_num, fanout, steps, duration):
  seed_ph = tf.placeholder(tf.int64, shape=[seed_num])
  sample = tf_euler.sample_fanout(seed_ph, [[0]]*steps, [fanout]*steps)
  sample_num = 0
  seed_generator = get_seed(NUM_NODES, seed_num)
  with tf.Session() as sess:
    start_t = time.time()
    # edges_tot = 0
    consumed_time = 0
    while time.time() - start_t < duration:
      seed = seed_generator.next()
      start_t0 = time.time()
      output = sess.run(sample, feed_dict={seed_ph : seed})
      consumed_time += time.time() - start_t0
      # edges_tot += sum([len(x) for x in output[0][1:]])
      sample_num += 1
    print consumed_time, sample_num, consumed_time / sample_num

test_sample_multihop(args.seed_num, args.fanout, args.steps, args.duration)