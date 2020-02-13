import tf_euler
import tensorflow as tf
import config

tf_euler.initialize_graph({'mode': 'Remote',
                           'zk_server': config.zk_addr,
                           'zk_path': config.zk_path})

import time
start_t = time.time()

print "generate seed"
seed = tf_euler.sample_node(
  10, 
  0
) 

with tf.Session() as sess:
    output = sess.run(seed)
    print output


print "duration:", time.time() - start_t

