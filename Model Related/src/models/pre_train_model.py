import math
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForMaskedLM
from sentence_transformers import SentenceTransformer, models, losses
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from data.util import tokenize_idiom


"""
Pre-train a model on some data.

Parameters:
    train_samples : list[InputExample]
        Samples to train on.
    dev_samples : list[InputExample]
        Samples used for evaluation.
    model_path : str
        Path to store the trained model at.
    tmp_path : str
        Path to store intermediate models at.
    model_checkpoint : str
        The model to build upon. Default is 'bert-base-multilingual-cased'
    tokenize_idioms : bool
        Whether to use a single token for each MWE. Default is False.
    batch_size : int
        Batch size. Default is 4
    num_epochs : int
        Number of epochs to train for. Deafult is 4.
    warmup : float
        Amount of the training data to use for warmup.

Returns:
    model : SentenceTransformer
        The fine-tuned model. It is also saved at the given path.
"""
def make_pre_train_model(train_samples, dev_samples, model_path, tmp_path,
        model_checkpoint='bert-base-multilingual-cased', tokenize_idioms=False,
        batch_size=4, num_epochs=4, warmup=0.1):

    # Create a transformer model from a pretrained checkpoint

    idiom_tokens = []
    if tokenize_idioms and isinstance(tokenize_idioms, list):
        idiom_tokens = [tokenize_idiom(idiom) for idiom in tokenize_idioms]
        
    model = AutoModelForMaskedLM.from_pretrained(model_checkpoint)
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint, use_fast=False, truncation=True)
    # Add all of the idiom tokens to the tokenizer
    if tokenize_idioms:
        tokenizer.add_tokens(idiom_tokens)
        model.resize_token_embeddings(len(tokenizer))

    model.save_pretrained(tmp_path)
    tokenizer.save_pretrained(tmp_path)


    word_embedding_model = models.Transformer(tmp_path)
    # Apply mean pooling to get one fixed sized sentence vector
    pooling_model = models.Pooling(
        word_embedding_model.get_word_embedding_dimension(),
        pooling_mode_mean_tokens=True,
        pooling_mode_cls_token=False,
        pooling_mode_max_tokens=False
    )

    tokenizer = AutoTokenizer.from_pretrained(
        tmp_path, 
        use_fast=False,
        max_length=510,
        force_download=True
    )

    model = SentenceTransformer(modules=[word_embedding_model, pooling_model])
    model._first_module().tokenizer = tokenizer

    # Train transformer model
        
    train_dataloader = DataLoader(train_samples, shuffle=True, batch_size=batch_size)
    train_loss = losses.CosineSimilarityLoss(model=model)
        
    evaluator = EmbeddingSimilarityEvaluator.from_input_examples(dev_samples, name='sts-dev')

    # Configure the training. 
    warmup_steps = math.ceil(len(train_dataloader) * num_epochs  * warmup) # By default 10% of train data for warm-up
    print("Warmup-steps: {}".format(warmup_steps), flush=True)

    # Train the model
    
    model.fit(train_objectives=[(train_dataloader, train_loss)],
        evaluator=evaluator,
        epochs=num_epochs,
        evaluation_steps=1000,
        warmup_steps=warmup_steps,
        output_path=model_path
    )

    return model