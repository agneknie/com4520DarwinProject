import re
import string
from torch.utils.data import Dataset
from data.util import tokenize_idiom, load_csv
from evaluation.get_similarities import get_similarities
from sentence_transformers import InputExample


"""
Dataset where samples contain two sentences and an optional similarity
"""
class IdiomDataset(Dataset):
    """
    Creates a list of sentence1s, sentence2s and similarities from the given dataset

    Parameters:
        csv_file : str
            Filepath containing the dataset to load. It should have at least columns: [sentence1, sentence2, Language].
        tokenize_idioms : bool
            Whether to use a single token for each MWE. Default is False.
        tokenize_idioms_ignore_case : bool
            Whether to ignore case when tokenizing idioms (otherwise only lowercase would be matched). Default is True.
        languages : list[str]
            List of languages to include. Default is ['EN', 'PT']
    """
    def __init__(self, csv_file, tokenize_idioms=False, tokenize_idioms_ignore_case=True, languages=['EN', 'PT']):
        header, data = load_csv(csv_file)
        if tokenize_idioms:
            header, data = self.tokenize_all_idioms(header, data, tokenize_idioms_ignore_case)

        self.sentence1s, self.sentence2s, self.similarities = [], [], []
        self.MWE1s, self.MWE2s = [], []
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

            # save all MWEs in the input so they can be used later for gloss, commonsense etc
            self.MWE1s.append(elem[header.index('MWE1')])
            idiom = elem[header.index('MWE1')]
            if tokenize_idioms:
                idiom = tokenize_idiom(idiom)
            if elem[header.index('MWE2')] == 'None':
                self.MWE2s.append(self.find_replacement(self.sentence1s[-1], self.sentence2s[-1], idiom))
            else:
                self.MWE2s.append(elem[header.index('MWE2')])

        if None in self.similarities:
            self.similarities = []
        assert len(self.sentence1s) == len(self.sentence2s)
        assert len(self.similarities) == 0 or len(self.similarities) == len(self.sentence1s)

    """
    Change all MWEs to be a single token
    """
    def tokenize_all_idioms(self, header, data, tokenize_idioms_ignore_case=True):
        if 'sentence1' in header:
            sentence1_idx = header.index('sentence1')
            sentence2_idx = header.index('sentence2')
        else:
            sentence1_idx = header.index('sentence_1')
            sentence2_idx = header.index('sentence_2')

        for elem in data:
            MWE1 = elem[header.index('MWE1')]
            MWE2 = elem[header.index('MWE2')]

            if MWE1 != 'None':
                elem[sentence1_idx] = re.sub(MWE1, tokenize_idiom(MWE1), elem[sentence1_idx], flags=re.I*tokenize_idioms_ignore_case)
            if MWE2 != 'None':
                elem[sentence2_idx] = re.sub(MWE2, tokenize_idiom(MWE2), elem[sentence2_idx], flags=re.I*tokenize_idioms_ignore_case)
        return header, data

    """
    Find the phrase that a MWE has been replaced with 
    """
    def find_replacement(self, str1, str2, phrase):
        str1 = str1.translate(str.maketrans('', '', string.punctuation))
        str2 = str2.translate(str.maketrans('', '', string.punctuation))
        
        start = str1.lower().find(phrase.lower())
        end = start + len(phrase)
        return re.sub(str1[:start] + '(.*)' + str1[end:], r'\1', str2, flags=re.I).lower()

    """
    Applies a transform to every sentence in the dataset

    Parameters:
        func : (list[str], list[str]) -> list[str]
            Takes a list of sentences and corresponding MWEs, should return a transformed list of sentences 
    """
    def transform(self, func):
        self.sentence1s = func(self.sentence1s, self.MWE1s)
        self.sentence2s = func(self.sentence2s, self.MWE2s)

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
        csv_file : str
            Filepath containing the dataset to load. It should match the training set format. 
        tokenize_idioms : bool
            Whether to use a single token for each MWE. Default is False.
        tokenize_idioms_ignore_case : bool
            Whether to ignore case when tokenizing idioms (otherwise only lowercase would be matched). Default is True.
        languages : list[str]
            List of languages to include. Default is ['EN', 'PT']
    """
    def __init__(self, model, csv_file, tokenize_idioms=False, tokenize_idioms_ignore_case=True, languages=['EN', 'PT']):
        header, data = load_csv(csv_file)
        if tokenize_idioms:
            header, data = self.tokenize_all_idioms(header, data, tokenize_idioms_ignore_case)

        self.sentence1s, self.sentence2s, self.similarities = [], [], []
        self.MWE1s, self.MWE2s = [], []
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

            # save all MWEs in the input so they can be used later for gloss, commonsense etc
            self.MWE1s.append(elem[header.index('MWE1')])
            idiom = elem[header.index('MWE1')]
            if tokenize_idioms:
                idiom = tokenize_idiom(idiom)
            if elem[header.index('MWE2')] == 'None':
                self.MWE2s.append(self.find_replacement(self.sentence1s[-1], self.sentence2s[-1], idiom))
            else:
                self.MWE2s.append(elem[header.index('MWE2')])

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
        csv_file : str
            Filepath containing the dataset to load. It should match the training set format. 
        tokenize_idioms : bool
            Whether to use a single token for each MWE. Default is False.
        tokenize_idioms_ignore_case : bool
            Whether to ignore case when tokenizing idioms (otherwise only lowercase would be matched). Default is True.
        languages : list[str]
            List of languages to include. Default is ['EN', 'PT']
    """
    def __init__(self, csv_file, tokenize_idioms=False, tokenize_idioms_ignore_case=True, languages=['EN', 'PT']):
        header, data = load_csv(csv_file)
        if tokenize_idioms:
            header, data = self.tokenize_all_idioms(header, data, tokenize_idioms_ignore_case)

        self.sentence1s, self.sentence2s, self.similarities = [], [], []
        self.MWE1s, self.MWE2s = [], []
        for elem in data:
            if elem[header.index('Language')] not in languages:
                continue

            if elem[header.index('sim')] != '1':
                continue
            self.similarities.append(float(elem[header.index('sim')]))
                
            self.sentence1s.append(elem[header.index('sentence_1')])
            self.sentence2s.append(elem[header.index('sentence_2')])

            # save all MWEs in the input so they can be used later for gloss, commonsense etc
            self.MWE1s.append(elem[header.index('MWE1')])
            idiom = elem[header.index('MWE1')]
            if tokenize_idioms:
                idiom = tokenize_idiom(idiom)
            if elem[header.index('MWE2')] == 'None':
                self.MWE2s.append(self.find_replacement(self.sentence1s[-1], self.sentence2s[-1], idiom))
            else:
                self.MWE2s.append(elem[header.index('MWE2')])

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
        csv_file : str
            Filepath containing the dataset to load. It should have at least columns: [sentence1, sentence2, Language].
        tokenize_idioms : bool
            Whether to use a single token for each MWE. Default is False.
        tokenize_idioms_ignore_case : bool
            Whether to ignore case when tokenizing idioms (otherwise only lowercase would be matched). Default is True.
        languages : list[str]
            List of languages to include. Default is ['EN', 'PT']
    """
    def __init__(self, csv_file, tokenize_idioms=False, tokenize_idioms_ignore_case=True, languages=['EN', 'PT']):
        header, data = load_csv(csv_file)
        if tokenize_idioms:
            header, data = self.tokenize_all_idioms(header, data, tokenize_idioms_ignore_case)

        self.anchors, self.positives, self.negatives = [], [], []
        self.MWE1s, self.MWE2s, self.MWE3s = [], [], []
        for elem in data:
            if elem[header.index('Language')] not in languages:
                continue
            if elem[header.index('sim')] != 'None':
                continue

            self.anchors.append(elem[header.index('sentence_1')])
            self.positives.append(elem[header.index('alternative_1')])
            self.negatives.append(elem[header.index('sentence_2')])

            # save all MWEs in the input so they can be used later for gloss, commonsense etc
            self.MWE1s.append(elem[header.index('MWE1')])
            idiom = elem[header.index('MWE1')]
            if tokenize_idioms:
                idiom = tokenize_idiom(idiom)
            self.MWE2s.append(self.find_replacement(self.anchors[-1], self.positives[-1], idiom))
            self.MWE3s.append(self.find_replacement(self.anchors[-1], self.negatives[-1], idiom))

        assert len(self.anchors) == len(self.negatives) and len(self.anchors) == len(self.positives)

    def transform(self, func):
        self.anchors = func(self.anchors, self.MWE1s)
        self.positives = func(self.positives, self.MWE2s)
        self.negatives = func(self.negatives, self.MWE3s)

    def __len__(self):
        return len(self.anchors)

    def __getitem__(self, idx):
        return InputExample(texts=[self.anchors[idx], self.positives[idx], self.negatives[idx]])



        
