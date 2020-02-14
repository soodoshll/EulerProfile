import tf_euler
import tensorflow as tf
import config
import time


tf_euler.initialize_graph({'mode': 'Remote',
                           'zk_server': config.zk_addr,
                           'zk_path': config.zk_path})

def test_sample(seed_num, fanout, steps):
  layers = [tf_euler.sample_node(seed_num, 0)]
  for i in range(steps):
    layers.append(tf_euler.sample_node_with_src(layers[-1], fanout))
  with tf.Session() as sess:
    start_t = time.time()
    output = sess.run(layers)
    # print outpu1t
    consumed_time = time.time() - start_t
    print "time: ", consumed_time

test_sample(2,2,10)