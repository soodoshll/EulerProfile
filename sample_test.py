import tf_euler
import tensorflow as tf
import config
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--seed_num', type=int)
parser.add_argument('--fanout', type=int)
parser.add_argument('--steps', type=int)
args = parser.parse_args()

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

test_sample(args.seed_num, args.fanout, args.steps)