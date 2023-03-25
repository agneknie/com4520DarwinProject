import os
import sys
import argparse
import numpy as np
import random
import torch

from models.fine_tune_model import fine_tune_model
from data.idiom_dataset import para_context_transform


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

parser.add_argument('--base-model', help='The model to fine tune', required=True)
parser.add_argument('--output-path', help='Path to store the final model at', required=True)
parser.add_argument('--train-file', help='Path to train data csv', required=True)
parser.add_argument('--dev-path', help='Path to dir containing dev data e.g. data/datasets/semeval.../EvaluationData', required=True)
parser.add_argument('--num-epochs', help='Number of epochs to train for', required=True, type=int)
parser.add_argument('--batch-size', help='Batch size', required=True, type=int)
parser.add_argument('--include-para-context', action='store_true', help='Append previous and next sentences')
parser.add_argument('--en', action='store_true', help='Train on english data')
parser.add_argument('--pt', action='store_true', help='Train on portuguese data')
parser.add_argument('--tokenize-idioms', action='store_true', help='Include extra tokens for idioms')
parser.add_argument('--seed', help='Random seed', required=True, type=int)
parser.set_defaults(en=False, pt=False, tokenize_idioms=False, include_para_context=False)

args = parser.parse_args()


if not args.en and not args.pt:
    raise Exception('Must choose at least one of English and Portuguese')
languages = ['EN'] * args.en + ['PT'] * args.pt

if args.include_para_context:
    transform = para_context_transform
else:
    transform = None

set_seed(args.seed)

# Train the model
model = fine_tune_model(
    args.base_model,
    args.output_path,
    args.train_file,
    dev_eval_path=args.dev_path,
    tokenize_idioms=args.tokenize_idioms,
    languages=languages,
    num_epochs=args.num_epochs,
    batch_size=args.batch_size,
    transform=transform
    )
