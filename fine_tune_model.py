import os
import sys
import argparse
import numpy as np
import random
import torch

from sentence_transformers import SentenceTransformer

sys.path.append( '/content/com4520DarwinProject/src' )
from data.pre_train_dataset import make_pre_train_dataset
from models.pre_train_model import make_pre_train_model
from data.extract_idioms import extract_idioms
from evaluation.evaluate import get_dev_results, format_results, save_eval_output
from models.fine_tune_model import fine_tune_model
from visualisation.plot import plot_spearman_epochs


def set_seed(seed: int):
    """
    Modified from : https://github.com/huggingface/transformers/blob/master/src/transformers/trainer_utils.py
    Helper function for reproducible behavior to set the seed in ``random``, ``numpy``, ``torch`` and/or ``tf`` (if
    installed).
    Args:
        seed (:obj:`int`): The seed to set.
    """
    random.seed(seed)
    np.random.seed(seed)
    
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    # ^^ safe to call this function even if cuda is not available

    ## From https://pytorch.org/docs/stable/notes/randomness.html
    torch.backends.cudnn.benchmark = False

    ## Might want to use the following, but set CUBLAS_WORKSPACE_CONFIG=:16:8
    # try : 
    #   torch.use_deterministic_algorithms(True)
    # except AttributeError: 
    #   torch.set_deterministic( True )
    

# Parse command line arguments 

parser = argparse.ArgumentParser()

parser.add_argument('--base_model', help='The model to fine tune', required=True)
parser.add_argument('--output_path', help='Path to store the final model at', required=True)
parser.add_argument('--train-file', help='Path to train data csv', required=True)
parser.add_argument('--num_epochs', help='Number of epochs to train for', required=True, type=int)
parser.add_argument('--en', action='store_true', help='Train on english data')
parser.add_argument('--pt', action='store_true', help='Train on portuguese data')
parser.add_argument('--tokenize-idioms', action='store_true', help='Include extra tokens for idioms')
parser.add_argument('--seed', help='Random seed', required=True, type=int)
parser.set_defaults(en=False, pt=False, tokenize_idioms=False)

args = parser.parse_args()

base_path = os.path.join(os.getcwd())
subtask_b_dataset_path = os.path.join(base_path, 'data', 'datasets', 'SemEval_2022_Task2_SubTaskB')

if not args.en and not args.pt:
    raise Exception('Must choose at least one of English and Portuguese')
languages = ['EN'] * args.en + ['PT'] * args.pt

set_seed(args.seed)


# Train the model

dev_eval_path = os.path.join(subtask_b_dataset_path, 'EvaluationData')

model = fine_tune_model(
    args.base_model_path,
    args.model_output_path,
    args.train_file,
    dev_eval_path=dev_eval_path,
    tokenize_idioms=args.tokenize_idioms,
    languages=languages,
    num_epochs=args.num_epochs
    )
