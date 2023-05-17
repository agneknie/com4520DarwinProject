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

    def get_individual_glosses(self, sentences, MWEs):
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


if __name__ == '__main__':
    import argparse
    from data.idiom import load_dataset
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('--n-glosses', type=int)
    parser.add_argument('input-file', type=str)
    parser.add_argument('output-file', type=str)
    parser.add_argument('--root', type=str, default='.')
    args = parser.parse_args()

    sys.path.append(args.root)

    glosses = Glosses(args.n_glosses)

    header, data = load_dataset(args.input_file, transform=glosses.get_individual_glosses)

    write_csv([header] + data, args.output_file)
