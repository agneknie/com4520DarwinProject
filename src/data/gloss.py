import os
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.corpus import wordnet as wn

from data.util import load_csv, write_csv

current_dir = os.path.dirname(os.path.realpath(__file__))


class Glosses:
    gloss_cache_file = os.path.join(current_dir, 'glosses.csv')
    n_glosses_to_save = 16

    def __init__(self, n_glosses):
        self.n_glosses = n_glosses
        if os.path.isfile(self.gloss_cache_file):
            header, data = load_csv(self.gloss_cache_file)
        else:
            header = ['Word'] + \
                [f'Gloss_{i}' for i in range(1, self.n_glosses_to_save+1)]
            data = []

        self.glosses = {}
        for row in data:
            self.glosses[row[header.index('Word')]] = [
                row[header.index(f'Gloss_{i}')]
                for i in range(1, self.n_glosses_to_save+1)
                if row[header.index(f'Gloss_{i}')] != 'None'
            ]

    def save_glosses(self):
        header = ['Word'] + \
            [f'Gloss_{i}' for i in range(1, self.n_glosses_to_save+1)]
        data = []
        for word, glosses in self.glosses.items():
            row = [word] + [self.glosses[word][i] if i <
                            len(self.glosses[word]) else 'None' for i in range(self.n_glosses_to_save)]
            data.append(row)

        write_csv([header] + data, self.gloss_cache_file)

    def get_gloss_transform(self, sentences, MWEs):
        gloss_strings = []
        for mwe in MWEs:
            words = mwe.lower().split(' ')
            gloss_string = ''
            for word in words:
                if word not in self.glosses:
                    self.glosses[word] = [synset.definition().capitalize()
                                          for synset in wn.synsets(word)]

                glosses = self.glosses[word]
                for i in range(0, min(self.n_glosses, len(glosses))):
                    gloss_string += self.glosses[word][i] + '. '
            gloss_strings.append(gloss_string)

        self.save_glosses()
        return [sentence + '[SEP]' + gloss for (sentence, gloss) in zip(sentences, gloss_strings)]

    # kind of a hacky way to use load_dataset transform, 
    # instead of returning sentences as expected we are returning a list of glosses for each sentence
    def get_gloss_list(self, sentences, MWEs):
        gloss_lists = []
        for mwe in MWEs:
            words = mwe.lower().split(' ')
            gloss_list = []
            for word in words:
                if word not in self.glosses:
                    self.glosses[word] = [synset.definition().capitalize()
                                          for synset in wn.synsets(word)]

                for i in range(0, self.n_glosses):
                    if len(self.glosses[word]) > i:
                        gloss_list.append(self.glosses[word][i])
                    else:
                        gloss_list.append('')

            gloss_lists.append(gloss_list)

        self.save_glosses()
        return gloss_lists
