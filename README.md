## Setup

All code was developed and tested on Nvidia V100 the following environment.

- Python 2.7
- opencv3
- scikit-image
- numpy
- tensorflow>=1.0
- cuda>=8.0
- cudnn>=5.0

Please download the data via the following external links.

* [Moving MNIST](https://www.dropbox.com/s/fpe24s1t94m87rn/moving-mnist-example.tar.gz?dl=0) is a dataset with two moving digits bouncing in a 64 by 64 area.
* [KTH Actions](https://www.dropbox.com/s/ppmob712dzgogly/kth_action.tar.gz?dl=0) is a human action dataset. This dataset contains frames from original videos. It selects the reasonable, predictable ones and resize them.


A full list of commands can be found in the script folder.
The training script has a number of command-line flags that you can use to configure the model architecture, hyperparameters, and input / output settings.
Below are the parameters about our model:

- `--model_name`: The model name. Default value is `e3d_lstm`.
- `--pretrained_model`: Directory to find our pretrained models. See below for the download instruction.
- `--num_hidden`: Comma separated number of units of e3d lstms
- `--filter_size`: Filter of a single e3d-lstm layer.
- `--layer_norm`: Whether to apply tensor layer norm.

`scheduled_sampling`, `sampling_stop_iter`, `sampling_start_value` and `sampling_changing_rate` are hyperparameters used for scheduled sampling in training. The standard parameters for training and testing are:

- `--is_training`: Is it training or testing.
- `--train_data_paths`, `--valid_data_paths`: Training and validation dataset path.
- `--gen_frm_dir`: Directory to store the prediction results.
- `--allow_gpu_growth`: Whether allows GPU to grow.
- `--input_length 10`: Input sequence length.
- `--total_length 20`: Input and output sequence length in total.


To test a model, set `--is_training False`.
