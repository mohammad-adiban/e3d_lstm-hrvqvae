from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import numpy as np
from src.data_provider import datasets_factory
from src.models.model_factory import Model
import src.trainer as trainer
from src.utils import preprocess
import tensorflow as tf

FLAGS = tf.app.flags.FLAGS
FLAGS.train_data_paths = '/path to train files (e.g /path/moving-mnist-train.npz) '
FLAGS.valid_data_paths = '/path to test files (e.gmoving-mnist-valid.npz) '
FLAGS.save_dir = '/path to checkpoints'
FLAGS.gen_frm_dir = '/path to save results'

FLAGS.is_training = True 
FLAGS.dataset_name =  'mnist'
FLAGS.input_length = 10
FLAGS.total_length =  20
FLAGS.img_width = 64
FLAGS.img_channel = 1
FLAGS.patch_size = 4
FLAGS.reverse_input = False

FLAGS.model_name =  'e3d_lstm'
FLAGS.pretrained_model =  ''
FLAGS.num_hidden = '64,64,64,64'
FLAGS.filter_size = 5
FLAGS.layer_norm = True

FLAGS.scheduled_sampling = True
FLAGS.sampling_stop_iter = 50000
FLAGS.sampling_start_value = 1.0
FLAGS.sampling_changing_rate = 0.00002

FLAGS.lr = 0.001
FLAGS.batch_size = 20 #8
FLAGS.max_iterations = 80000
FLAGS.display_interval = 1
FLAGS.test_interval = 1000
FLAGS.snapshot_interval = 10000 #1000 number of iters saving models.
FLAGS.num_save_samples = 10 #number of sequences to be saved.
FLAGS.n_gpu = 1
FLAGS.allow_gpu_growth = True 




def schedule_sampling(eta, itr):
    """Gets schedule sampling parameters for training."""
    zeros = np.zeros(
      (FLAGS.batch_size, FLAGS.total_length - FLAGS.input_length - 1,
       FLAGS.img_width // FLAGS.patch_size, FLAGS.img_width // FLAGS.patch_size,
       FLAGS.patch_size**2 * FLAGS.img_channel))
    if not FLAGS.scheduled_sampling:
        return 0.0, zeros

    if itr < FLAGS.sampling_stop_iter:
        eta -= FLAGS.sampling_changing_rate
    else:
        eta = 0.0
    random_flip = np.random.random_sample(
      (FLAGS.batch_size, FLAGS.total_length - FLAGS.input_length - 1))
    true_token = (random_flip < eta)
    ones = np.ones(
      (FLAGS.img_width // FLAGS.patch_size, FLAGS.img_width // FLAGS.patch_size,
       FLAGS.patch_size**2 * FLAGS.img_channel))
    zeros = np.zeros(
      (FLAGS.img_width // FLAGS.patch_size, FLAGS.img_width // FLAGS.patch_size,
       FLAGS.patch_size**2 * FLAGS.img_channel))
    real_input_flag = []
    for i in range(FLAGS.batch_size):
        for j in range(FLAGS.total_length - FLAGS.input_length - 1):
            if true_token[i, j]:
                real_input_flag.append(ones)
            else:
                real_input_flag.append(zeros)
    real_input_flag = np.array(real_input_flag)
    real_input_flag = np.reshape(
      real_input_flag,
      (FLAGS.batch_size, FLAGS.total_length - FLAGS.input_length - 1,
       FLAGS.img_width // FLAGS.patch_size, FLAGS.img_width // FLAGS.patch_size,
       FLAGS.patch_size**2 * FLAGS.img_channel))
    return eta, real_input_flag



def train_wrapper(model):
    if FLAGS.pretrained_model:
        model.load(FLAGS.pretrained_model)
    # load data
    train_input_handle, test_input_handle = datasets_factory.data_provider(
      FLAGS.dataset_name,
      FLAGS.train_data_paths,
      FLAGS.valid_data_paths,
      FLAGS.batch_size * FLAGS.n_gpu,
      FLAGS.img_width,
      seq_length=FLAGS.total_length,
      is_training=True)

    eta = FLAGS.sampling_start_value

    for itr in range(1, FLAGS.max_iterations + 1):
        if train_input_handle.no_batch_left():
            train_input_handle.begin(do_shuffle=True)
        ims = train_input_handle.get_batch()
        if FLAGS.dataset_name == 'penn':
            ims = ims['frame']
        ims = preprocess.reshape_patch(ims, FLAGS.patch_size)

        eta, real_input_flag = schedule_sampling(eta, itr)

        trainer.train(model, ims, real_input_flag, FLAGS, itr)

        if itr % FLAGS.snapshot_interval == 0:
            model.save(itr)

        if itr % FLAGS.test_interval == 0:
            trainer.test(model, test_input_handle, FLAGS, itr)

        train_input_handle.next()



def test_wrapper(model):
    model.load(FLAGS.pretrained_model)
    test_input_handle = datasets_factory.data_provider(
        FLAGS.dataset_name,
        FLAGS.train_data_paths,
        FLAGS.valid_data_paths,
        FLAGS.batch_size * FLAGS.n_gpu,
        FLAGS.img_width,
        is_training=False)
    trainer.test(model, test_input_handle, FLAGS, 'test_result')



# print(FLAGS.reverse_input)
#if tf.gfile.Exists(FLAGS.save_dir):
#    tf.gfile.DeleteRecursively(FLAGS.save_dir)
#tf.gfile.MakeDirs(FLAGS.save_dir)
#if tf.gfile.Exists(FLAGS.gen_frm_dir):
#    tf.gfile.DeleteRecursively(FLAGS.gen_frm_dir)
#tf.gfile.MakeDirs(FLAGS.gen_frm_dir)

gpu_list = np.asarray(
  os.environ.get('CUDA_VISIBLE_DEVICES', '-1').split(','), dtype=np.int32)
FLAGS.n_gpu = len(gpu_list)
print('Initializing models')

model = Model(FLAGS)



if FLAGS.is_training:
    train_wrapper(model)
else:
    test_wrapper(model)


