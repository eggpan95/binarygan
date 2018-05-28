"""Define configuration variables in experiment, model and training levels.

Quick Setup
===========
Change the values in the dictionary `SETUP` for a quick setup.
Documentation is provided right after each key.

Configuration
=============
More configuration options are provided. Four dictionaries `EXP_CONFIG`,
`DATA_CONFIG`, `MODEL_CONFIG` and `TRAIN_CONFIG` define experiment-, data-,
model- and training-related configuration variables, respectively.

Note that the automatically-determined experiment name is based only on the
values defined in the dictionary `SETUP`, so remember to provide the experiment
name manually if you have changed the configuration so that you won't overwrite
existing experiment directories.
"""
import os
import shutil
import distutils.dir_util
import importlib
import tensorflow as tf

# Quick setup
SETUP = {
    'exp_name': 'test',
    # The experiment name. Also the name of the folder that will be created
    # in './exp/' and all the experiment-related files are saved in that
    # folder. None to determine automatically. The automatically-
    # determined experiment name is based only on the values defined in the
    # dictionary `SETUP`, so remember to provide the experiment name manually
    # (so that you won't overwrite a trained model).

    'training_data': 'herman_mnist_x_binarized',
    # Filename of the training data. The training data can be loaded from a npy
    # file in the hard disk or from the shared memory using SharedArray package.
    # Note that the data will be reshaped to (-1, num_bar, num_timestep,
    # num_pitch, num_track) and remember to set these variable to proper values,
    # which are defined in `MODEL_CONFIG`.

    'training_data_location': 'sa',
    # Location of the training data. 'hd' to load from a npy file stored in the
    # hard disk. 'sa' to load from shared array using SharedArray package.

    'gpu': '0',
    # The GPU index in os.environ['CUDA_VISIBLE_DEVICES'] to use.

    'prefix': 'wgan-gp-bmnist',
    # Prefix for the experiment name. Useful when training with different
    # training data to avoid replacing the previous experiment outputs.

    'sample_along_training': True,
    # True to generate samples along the training process. False for nothing.

    'evaluate_along_training': True,
    # True to run evaluation along the training process. False for nothing.

    'verbose': False,
    # True to print each batch details to stdout. False to print once an epoch.

    'two_stage_training': True,
    # True to train the model in a two-stage training setting. False to
    # train the model in an end-to-end manner.

    'training_phase': 'pretrain',
    # {'train', 'pretrain'}
    # The training phase in a two-stage training setting. Only effective
    # when `two_stage_training` is True.

    'joint_training': False,
    # True to train the generator and the refiner jointly. Only effective
    # when `two_stage_training` is True and `training_phase` is 'train'.

    'pretrained_dir': None,
    # The directory containing the pretrained model. None to retrain the
    # model from scratch.

    'first_stage_dir': None,
    # The directory containing the pretrained first-stage model. None to
    # determine automatically (assuming default `exp_name`). Only effective
    # when `two_stage_training` is True and `training_phase` is 'train'.

    'preset_g': 'mlp_real',
    # {'proposed', 'proposed_small', None}
    # Use a preset network architecture for the generator or set to None and
    # setup `MODEL_CONFIG['net_g']` to define the network architecture.

    'preset_d': 'mlp',
    # {'proposed', 'proposed_small', 'ablated', 'baseline', None}
    # Use a preset network architecture for the discriminator or set to None
    # and setup `MODEL_CONFIG['net_d']` to define the network architecture.

    'preset_r': 'proposed_round',
    # {'proposed_round', 'proposed_bernoulli'}
    # Use a preset network architecture for the refiner or set to None and
    # setup `MODEL_CONFIG['net_r']` to define the network architecture.
}

#===============================================================================
#=========================== TensorFlow Configuration ==========================
#===============================================================================
os.environ['CUDA_VISIBLE_DEVICES'] = SETUP['gpu']
TF_CONFIG = tf.ConfigProto()
TF_CONFIG.gpu_options.allow_growth = True

#===============================================================================
#========================== Experiment Configuration ===========================
#===============================================================================
EXP_CONFIG = {
    'exp_name': None,
    'two_stage_training': None,
    'pretrained_dir': None,
    'first_stage_dir': None,
}

if EXP_CONFIG['two_stage_training'] is None:
    EXP_CONFIG['two_stage_training'] = SETUP['two_stage_training']
if EXP_CONFIG['pretrained_dir'] is None:
    EXP_CONFIG['pretrained_dir'] = SETUP['pretrained_dir']

# Set default experiment name
if EXP_CONFIG['exp_name'] is None:
    if SETUP['exp_name'] is not None:
        EXP_CONFIG['exp_name'] = SETUP['exp_name']
    elif not SETUP['two_stage_training']:
        EXP_CONFIG['exp_name'] = '_'.join(
            (SETUP['prefix'], 'end2end', 'g', SETUP['preset_g'], 'd',
             SETUP['preset_d']) #, 'r', SETUP['preset_r'])
        )
    elif SETUP['training_phase'] == 'pretrain':
        EXP_CONFIG['exp_name'] = '_'.join(
            (SETUP['prefix'], SETUP['training_phase'], 'g', SETUP['preset_g'],
             'd', SETUP['preset_d'])
        )
    elif SETUP['training_phase'] == 'train':
        if SETUP['joint_training']:
            EXP_CONFIG['exp_name'] = '_'.join(
                (SETUP['prefix'], SETUP['training_phase'], 'joint', 'g',
                 SETUP['preset_g'], 'd', SETUP['preset_d'], 'r',
                 SETUP['preset_r'])
            )
        else:
            EXP_CONFIG['exp_name'] = '_'.join(
                (SETUP['prefix'], SETUP['training_phase'], 'g',
                 SETUP['preset_g'], 'd', SETUP['preset_d'], 'r',
                 SETUP['preset_r'])
            )

# Set default pretained model directory
if EXP_CONFIG['first_stage_dir'] is None:
    if SETUP['first_stage_dir'] is not None:
        EXP_CONFIG['first_stage_dir'] = SETUP['first_stage_dir']
    else:
        EXP_CONFIG['first_stage_dir'] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'exp',
            '_'.join((SETUP['prefix'], 'pretrain', 'g', SETUP['preset_g'],
                      'd', SETUP['preset_d'])), 'checkpoints'
        )

#===============================================================================
#============================= Data Configuration ==============================
#===============================================================================
DATA_CONFIG = {
    'training_data': None,
    'training_data_location': None,
}

if DATA_CONFIG['training_data'] is None:
    DATA_CONFIG['training_data'] = SETUP['training_data']
if DATA_CONFIG['training_data_location'] is None:
    DATA_CONFIG['training_data_location'] = SETUP['training_data_location']

#===============================================================================
#=========================== Training Configuration ============================
#===============================================================================
TRAIN_CONFIG = {
    'sample_along_training': None,
    'evaluate_along_training': None,
    'verbose': None,
    'two_stage_training': None,
    'training_phase': None,
    'num_epoch': 50,
    'slope_annealing_rate': 1.1,
}

if TRAIN_CONFIG['sample_along_training'] is None:
    TRAIN_CONFIG['sample_along_training'] = SETUP['sample_along_training']
if TRAIN_CONFIG['evaluate_along_training'] is None:
    TRAIN_CONFIG['evaluate_along_training'] = SETUP['evaluate_along_training']
if TRAIN_CONFIG['training_phase'] is None:
    TRAIN_CONFIG['training_phase'] = SETUP['training_phase']
if TRAIN_CONFIG['verbose'] is None:
    TRAIN_CONFIG['verbose'] = SETUP['verbose']

#===============================================================================
#============================= Model Configuration =============================
#===============================================================================
MODEL_CONFIG = {
    # Models
    'joint_training': None,

    # Parameters
    'batch_size': 64, # Note: tf.layers.conv3d_transpose requires a fixed batch
                      # size in TensorFlow < 1.6
    'gan': {
        'type': 'wgan-gp', # 'gan', 'wgan'
        'clip_value': .01,
        'gp_coefficient': 10.
    },
    'optimizer': {
        # Parameters for Adam optimizers
        'lr': .002,
        'beta1': .5,
        'beta2': .9,
        'epsilon': 1e-8
    },

    # Data
    'out_width': 28,
    'out_height': 28,
    'out_channel': 1,

    # Network architectures (define them here if not using the presets)
    'net_g': None,
    'net_d': None,
    'net_r': None,

    # Samples
    'num_sample': 32,
    'sample_grid': (4, 8),

    # Directories
    'checkpoint_dir': None,
    'sample_dir': None,
    'eval_dir': None,
    'log_dir': None,
    'src_dir': None,
}

if MODEL_CONFIG['joint_training'] is None:
    MODEL_CONFIG['joint_training'] = SETUP['joint_training']

# Import preset network architectures
if MODEL_CONFIG['net_g'] is None:
    IMPORTED = importlib.import_module('.'.join((
        'bgan.mnist.presets', 'generator', SETUP['preset_g']
    )))
    MODEL_CONFIG['net_g'] = IMPORTED.NET_G
if MODEL_CONFIG['net_d'] is None:
    IMPORTED = importlib.import_module('.'.join((
        'bgan.mnist.presets', 'discriminator', SETUP['preset_d']
    )))
    MODEL_CONFIG['net_d'] = IMPORTED.NET_D
if MODEL_CONFIG['net_r'] is None:
    IMPORTED = importlib.import_module('.'.join((
        'bgan.mnist.presets', 'refiner', SETUP['preset_r']
    )))
    MODEL_CONFIG['net_r'] = IMPORTED.NET_R

# Set default directories
if MODEL_CONFIG['checkpoint_dir'] is None:
    MODEL_CONFIG['checkpoint_dir'] = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'exp',
        EXP_CONFIG['exp_name'], 'checkpoints'
    )
if MODEL_CONFIG['sample_dir'] is None:
    MODEL_CONFIG['sample_dir'] = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'exp',
        EXP_CONFIG['exp_name'], 'samples'
    )
if MODEL_CONFIG['eval_dir'] is None:
    MODEL_CONFIG['eval_dir'] = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'exp',
        EXP_CONFIG['exp_name'], 'eval'
    )
if MODEL_CONFIG['log_dir'] is None:
    MODEL_CONFIG['log_dir'] = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'exp',
        EXP_CONFIG['exp_name'], 'logs'
    )
if MODEL_CONFIG['src_dir'] is None:
    MODEL_CONFIG['src_dir'] = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'exp',
        EXP_CONFIG['exp_name'], 'src'
    )

#===============================================================================
#=================== Make directories & Backup source code =====================
#===============================================================================
# Make sure directories exist
for path in (MODEL_CONFIG['checkpoint_dir'], MODEL_CONFIG['sample_dir'],
             MODEL_CONFIG['eval_dir'], MODEL_CONFIG['log_dir'],
             MODEL_CONFIG['src_dir']):
    if not os.path.exists(path):
        os.makedirs(path)

# Backup source code
for path in os.listdir(os.path.dirname(os.path.realpath(__file__))):
    if os.path.isfile(path):
        if path.endswith('.py'):
            shutil.copyfile(
                os.path.basename(path),
                os.path.join(MODEL_CONFIG['src_dir'], os.path.basename(path))
            )

distutils.dir_util.copy_tree(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bgan'),
    os.path.join(MODEL_CONFIG['src_dir'], 'bgan')
)