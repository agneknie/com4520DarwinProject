import os
import gzip
import csv
from sentence_transformers import util
from sentence_transformers.readers import InputExample
from datasets import load_dataset

"""
Create a dataset containing general STS data
EN: SBERT STS Benchmark Dataset
PT: ASSIN2 Dataset

Parameters:
    data_path : str
        Path to the directory to store datasets in
    languages : list[str]
        List of languages to include. Default is ['EN', 'PT']

Returns:
    train_samples : list[InputExample]
    dev_samples : list[InputExample]
    test_samples : list[InputExample]
"""
def make_pre_train_dataset(data_path, languages=['EN', 'PT']):
    train_samples, dev_samples, test_samples = [], [], []

    # English 
    if 'EN' in languages:
        sts_dataset_path = os.path.join(data_path, 'datasets', 'stsbenchmark.tsv.gz')
        if not os.path.exists(sts_dataset_path):
            util.http_get('https://sbert.net/datasets/stsbenchmark.tsv.gz', sts_dataset_path)

        with gzip.open(sts_dataset_path, 'rt', encoding='utf8') as fIn:
            reader = csv.DictReader(fIn, delimiter='\t', quoting=csv.QUOTE_NONE)
            for row in reader:
                score = float(row['score']) / 5.0  # Normalize score to range 0 ... 1
                inp_example = InputExample(texts=[row['sentence1'], row['sentence2']], label=score)

                if row['split'] == 'dev':
                    dev_samples.append(inp_example)
                elif row['split'] == 'test':
                    test_samples.append(inp_example)
                else:
                    train_samples.append(inp_example)

    # Portuguese data
    if 'PT' in languages:
        for split in [ 'train', 'validation', 'test' ] :
            dataset = load_dataset( 'assin2', split=split )
            for elem in dataset :
                ## {'entailment_judgment': 1, 'hypothesis': 'Uma criança está segurando uma pistola de água', 'premise': 'Uma criança risonha está segurando uma pistola de água e sendo espirrada com água', 'relatedness_score': 4.5, 'sentence_pair_id': 1}
                score = float( elem['relatedness_score'] ) / 5.0 # Normalize score to range 0 ... 1
                inp_example = InputExample(texts=[elem['hypothesis'], elem['premise']], label=score)
                if split == 'validation':
                    dev_samples.append(inp_example)
                elif split == 'test':
                    test_samples.append(inp_example)
                elif split == 'train' :
                    train_samples.append(inp_example)
                else :
                    raise Exception( "Unknown split. Should be one of ['train', 'test', 'validation']." )

    return train_samples, dev_samples, test_samples