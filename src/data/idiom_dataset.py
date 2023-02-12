import re
import string
from torch.utils.data import Dataset
from data.util import tokenize_idiom, load_csv, remove_punctuation
from evaluation.get_similarities import get_similarities
from sentence_transformers import InputExample


"""
    Load a training, dev or evaluation dataset.
    Optionally apply tokenization and/or a custom transform function to every sentence

    Parameters:
        csv_file : str
            Filepath containing the dataset to load. It should have at least columns: [sentence1, sentence2, Language].
        tokenize_idioms : bool
            Whether to use a single token for each MWE. Default is False.
        tokenize_idioms_ignore_case : bool
            Whether to ignore case when tokenizing idioms (otherwise only lowercase would be matched). Default is True.
        transform : (list[str], list[str], list[str]) -> list[str]
            Takes a list of sentences and corresponding MWEs and languages, should return a transformed list of sentences 
        languages : list[str]
            List of languages to include. Default is ['EN', 'PT']
"""
def load_dataset(csv_file, tokenize_idioms=False, tokenize_idioms_ignore_case=True, transform=None, languages=['EN', 'PT']):
    header, data = load_csv(csv_file)
    # break down the data into sentences
    ids = []
    columns = []
    sentences = []
    langs = []
    MWEs = []
    for elem in data:
        if elem[header.index('Language')] not in languages:
            continue
        for column in [
            'sentence1',
            'sentence2',
            'sentence_1',
            'sentence_2',
            'alternative_1',
            'alternative_2'
        ]:
            if column in header:
                sentence = elem[header.index(column)]
                if len(sentence) == 0:
                    continue
                MWE = elem[header.index('MWE1')]

                # check if the MWE has been replaced with a paraphrase in this sentence
                # (i.e. if this is an alternative sentence)
                MWE_replace = None
                sentence_copy = remove_punctuation(sentence.lower())
                MWE_copy = remove_punctuation(MWE.lower())
                if MWE_copy not in sentence_copy:
                    # get the original sentence (where the idiom has not been replaced)
                    if 'sentence1' in header:
                        sentence_base = elem[header.index('sentence1')]
                    else:
                        sentence_base = elem[header.index('sentence_1')]
                    sentence_base = remove_punctuation(sentence_base.lower())
                    start = sentence_base.find(MWE.lower())
                    end = start + len(MWE)
                    MWE_replace = re.sub(sentence_base[:start] + '(.*)' + sentence_base[end:], r'\1', sentence_copy, flags=re.I)

                if tokenize_idioms:
                    sentence = re.sub(MWE, tokenize_idiom(MWE), sentence, flags=re.I*tokenize_idioms_ignore_case)

                ids.append(elem[header.index('ID')])
                columns.append(column)
                sentences.append(sentence)
                langs.append(elem[header.index('Language')])
                MWEs.append(MWE if MWE_replace is None else MWE_replace)

    if transform is not None:
        sentences = transform(sentences, MWEs, langs)

    # write the transformed sentences back to the data
    for id, column, sentence in zip(ids, columns, sentences):
        elem = [row for row in data if row[header.index('ID')] == id][0]
        elem[header.index(column)] = sentence

    return header, data


"""
Dataset where samples contain two sentences and an optional similarity
"""
class IdiomDataset(Dataset):
    """
    Creates a list of sentence1s, sentence2s and similarities from the given dataset

    Parameters:
        header : list[str]
            Column headers of the csv file
        data : list[list[str]]
            Data loaded from the csv file
        languages : list[str]
            List of languages to include. Default is ['EN', 'PT']
    """
    def __init__(self, header, data, languages=['EN', 'PT']):
        self.sentence1s, self.sentence2s, self.similarities = [], [], []
        for elem in data:
            if elem[header.index('Language')] not in languages:
                continue
            if 'sim' in header:
                if elem[header.index('sim')] == 'None':
                    self.similarities.append(None)
                else:
                    self.similarities.append(float(elem[header.index('sim')]))

            if 'sentence1' in header and 'sentence2' in header:
                self.sentence1s.append(elem[header.index('sentence1')])
                self.sentence2s.append(elem[header.index('sentence2')])
            # in train data the column has an underscore
            elif 'sentence_1' in header and 'sentence_2' in header:
                self.sentence1s.append(elem[header.index('sentence_1')])
                self.sentence2s.append(elem[header.index('sentence_2')])
            # this should never happen
            else:
                continue

        if None in self.similarities:
            self.similarities = []
        assert len(self.sentence1s) == len(self.sentence2s)
        assert len(self.similarities) == 0 or len(self.similarities) == len(self.sentence1s)

    def __len__(self):
        return len(self.sentence1s)

    def __getitem__(self, idx):
        if len(self.similarities) == 0:
            return InputExample(texts=[self.sentence1s[idx], self.sentence2s[idx]])
        else:
            return InputExample(texts=[self.sentence1s[idx], self.sentence2s[idx]], label=self.similarities[idx])



class SelfEvaluatedDataset(IdiomDataset):
    """
    Creates a list of sentence1s, sentence2s and similarities from the given dataset

    Parameters:
        model : SentenceTransformer
            Model to evaluate unlabelled sentences.
        header : list[str]
            Column headers of the csv file
        data : list[list[str]]
            Data loaded from the csv file
        languages : list[str]
            List of languages to include. Default is ['EN', 'PT']
    """
    def __init__(self, model, header, data, languages=['EN', 'PT']):
        self.sentence1s, self.sentence2s, self.similarities = [], [], []
        for elem in data:
            if elem[header.index('Language')] not in languages:
                continue

            if elem[header.index('sim')] == 'None':
                sentence1 = elem[header.index('alternative_1')]
                sentence2 = elem[header.index('alternative_2')]
                
                sims = get_similarities([sentence1], [sentence2], model)
                self.similarities.append(sims[0])
            else:
                self.similarities.append(float(elem[header.index('sim')]))
            
            self.sentence1s.append(elem[header.index('sentence_1')])
            self.sentence2s.append(elem[header.index('sentence_2')])

        assert len(self.sentence1s) == len(self.sentence2s)
        assert len(self.similarities) == 0 or len(self.similarities) == len(self.sentence1s)


"""
Dataset where samples contain two sentences and an optional similarity
"""
class PositivesDataset(IdiomDataset):
    """
    Creates a list of sentence1s, sentence2s and similarities from the given dataset.
    Only includes samples that have a similarity of 1.

    Parameters:
        header : list[str]
            Column headers of the csv file
        data : list[list[str]]
            Data loaded from the csv file
        languages : list[str]
            List of languages to include. Default is ['EN', 'PT']
    """
    def __init__(self, header, data, languages=['EN', 'PT']):
        self.sentence1s, self.sentence2s, self.similarities = [], [], []
        for elem in data:
            if elem[header.index('Language')] not in languages:
                continue

            if elem[header.index('sim')] != '1':
                continue
            self.similarities.append(float(elem[header.index('sim')]))
                
            self.sentence1s.append(elem[header.index('sentence_1')])
            self.sentence2s.append(elem[header.index('sentence_2')])

        assert len(self.sentence1s) == len(self.sentence2s)
        assert len(self.similarities) == 0 or len(self.similarities) == len(self.sentence1s)


"""
Dataset where each sample contains an anchor sentence, a positive example and a negative example
"""
class TripletDataset(IdiomDataset):
    """
    Creates a list of anchor sentences, positive sentences and negative sentences from the dataset.
    Expects the data to be as follows:
        sentence_1: anchor (contains MWE)
        sentence_2: negative (incorrect paraphrase)
        alternative_1: positive (correct paraphrase)
        alternative_2: negative (incorrect paraphrase)

    Parameters:
        header : list[str]
            Column headers of the csv file
        data : list[list[str]]
            Data loaded from the csv file
        languages : list[str]
            List of languages to include. Default is ['EN', 'PT']
    """
    def __init__(self, header, data, languages=['EN', 'PT']):
        self.anchors, self.positives, self.negatives = [], [], []
        for elem in data:
            if elem[header.index('Language')] not in languages:
                continue
            if elem[header.index('sim')] != 'None':
                continue

            self.anchors.append(elem[header.index('sentence_1')])
            self.positives.append(elem[header.index('alternative_1')])
            self.negatives.append(elem[header.index('sentence_2')])


        assert len(self.anchors) == len(self.negatives) and len(self.anchors) == len(self.positives)

    def __len__(self):
        return len(self.anchors)

    def __getitem__(self, idx):
        return InputExample(texts=[self.anchors[idx], self.positives[idx], self.negatives[idx]])



        
