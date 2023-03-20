import math
import os
from sentence_transformers import SentenceTransformer
from sentence_transformers.losses import MultipleNegativesRankingLoss, TripletLoss, CosineSimilarityLoss
from torch.utils.data import DataLoader
from data.idiom_dataset import load_dataset, PositivesDataset, TripletDataset, SelfEvaluatedDataset, IdiomDataset
from evaluation.idiom_evaluator import IdiomEvaluator


"""
Fine-tune a model on some data.
Uses MultipleNegativesRankingLoss and TripletLoss.

Parameters:
    model_path : str
        Path to the directory where the pre-trained model is stored.
    output_path : str
        Path to store the new fine-tuned model in.
    train_file : str
        Path to the file containing the training data.
    tokenize_idioms : bool
        Whether to use a single token for each MWE. Default is False.
    languages : list[str]
        List of languages to include. Default is ['EN', 'PT']
    dev_eval_path : str
        Path to the directory containing dev and eval datasets
    batch_size : int
        Batch size. Default is 4
    num_epochs : int
        Number of epochs to train for. Default is 4.
    warmup : float
        Amount of the training data to use for warmup.
    checkpoint_path : str
        Path to save model checkpoints at. Default is None.
    checkpoint_save_steps : int
        How often to save a checkpoint. Default is None. If None and `checkpoint_path` is not None 
        then a checkpoint is saved after every epoch.
    transform : (list[str], list[str]) -> list[str]
        Takes a list of sentences and corresponding MWEs, should return a transformed list of sentences 

Returns:
    model : SentenceTransformer
        The fine-tuned model. It is also saved at the given path.
"""
def fine_tune_model(model_path, output_path, train_file,
        tokenize_idioms=False, languages=['EN', 'PT'], dev_eval_path=None,
        batch_size=4, num_epochs=4, warmup=0.1, checkpoint_path=None, checkpoint_save_steps=None,
        transform=None):
    
    model = SentenceTransformer(model_path)
    header, data = load_dataset(train_file, tokenize_idioms=tokenize_idioms, transform=transform, languages=languages)

    positives_dataset = PositivesDataset(header, data, languages=languages)
    positives_dataloader = DataLoader(positives_dataset,  shuffle=True, batch_size=batch_size)
    postitives_loss = MultipleNegativesRankingLoss(model=model)
    print('First positives sample: ',
        ' '.join(model.tokenizer.tokenize(positives_dataset[0].texts[0])), '\n',
        ' '.join(model.tokenizer.tokenize(positives_dataset[0].texts[1])))
    print('Num positives samples: ', len(positives_dataset))

    triplets_dataset = TripletDataset(header, data, languages=languages)
    triplets_dataloader = DataLoader(triplets_dataset,  shuffle=True, batch_size=batch_size)
    triplets_loss = TripletLoss(model=model)
    print('First triplet sample: ', 
        ' '.join(model.tokenizer.tokenize(triplets_dataset[0].texts[0])), '\n',
        ' '.join(model.tokenizer.tokenize(triplets_dataset[0].texts[1])), '\n',
        ' '.join(model.tokenizer.tokenize(triplets_dataset[0].texts[2])))
    print('Num triplet samples: ', len(triplets_dataset))

    print('Total samples: ', len(positives_dataset) + len(triplets_dataset))

    evaluator = None
    if dev_eval_path is not None:
        evaluator = IdiomEvaluator(
            dev_eval_path, 
            save_path=os.path.join(output_path, 'eval'),
            tokenize_idioms=tokenize_idioms,
            transform=transform,
            languages=languages
            )

    train_objectives = [(positives_dataloader, postitives_loss), (triplets_dataloader, triplets_loss)]
    if checkpoint_path is not None and checkpoint_save_steps is None:
        checkpoint_save_steps = min([len(obj[0]) for obj in train_objectives])

    warmup_steps = math.ceil(len(positives_dataloader) * num_epochs * warmup) # By default 10% of train data for warm-up
    print('Num warmup steps: ', warmup_steps)

    # Train the model
    model.fit(train_objectives=train_objectives,
        evaluator=evaluator,
        epochs=num_epochs,
        evaluation_steps=0,
        warmup_steps=warmup_steps,
        output_path=output_path,
        checkpoint_path=checkpoint_path,
        checkpoint_save_steps=checkpoint_save_steps
        )

    return model


"""
Fine-tune a model on some data.
Uses CosineSimilarityLoss.

Parameters:
    model_path : str
        Path to the directory where the pre-trained model is stored.
    output_path : str
        Path to store the new fine-tuned model in.
    train_file : str
        Path to the file containing the training data.
    tokenize_idioms : bool
        Whether to use a single token for each MWE. Default is False.
    languages : list[str]
        List of languages to include. Default is ['EN', 'PT']
    batch_size : int
        Batch size. Default is 4
    num_epochs : int
        Number of epochs to train for. Default is 4.
    warmup : float
        Amount of the training data to use for warmup.
    checkpoint_path : str
        Path to save model checkpoints at. Default is None.
    checkpoint_save_steps : int
        How often to save a checkpoint. Default is None. If None and `checkpoint_path` is not None 
        then a checkpoint is saved after every epoch.
    transform : (list[str], list[str]) -> list[str]
        Takes a list of sentences and corresponding MWEs, should return a transformed list of sentences 

Returns:
    model : SentenceTransformer
        The fine-tuned model. It is also saved at the given path.
"""
def fine_tune_model_baseline(model_path, output_path, train_file,
        tokenize_idioms=False, languages=['EN', 'PT'],
        batch_size=4, num_epochs=4, warmup=0.1, checkpoint_path=None, checkpoint_save_steps=None,
        transform=None):
    
    model = SentenceTransformer(model_path)
    header, data = load_dataset(train_file, tokenize_idioms=tokenize_idioms, transform=transform, languages=languages)

    dataset = SelfEvaluatedDataset(header, data, languages=languages)
    dataloader = DataLoader(dataset,  shuffle=True, batch_size=batch_size)
    loss = CosineSimilarityLoss(model=model)
    print('First sample: ',
        ' '.join(model.tokenizer.tokenize(dataset[0].texts[0])),
        ' '.join(model.tokenizer.tokenize(dataset[0].texts[1])))
    print('Num training samples: ', len(dataset))

    train_objectives = [(dataloader, loss)]
    if checkpoint_path is not None and checkpoint_save_steps is None:
        checkpoint_save_steps = min([len(obj[0]) for obj in train_objectives])

    warmup_steps = math.ceil(len(dataloader) * num_epochs * warmup) # By default 10% of train data for warm-up
    print('Num warmup steps: ', warmup_steps)

    # Train the model
    model.fit(train_objectives=train_objectives,
        evaluator=None,
        epochs=num_epochs,
        evaluation_steps=0,
        warmup_steps=warmup_steps,
        output_path=output_path,
        checkpoint_path=checkpoint_path,
        checkpoint_save_steps=checkpoint_save_steps
        )

    return model