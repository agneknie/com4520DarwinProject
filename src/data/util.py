"""
Utility functions
"""
import re
import csv
import string


def load_csv(path):
    header = None
    data = list()
    with open(path, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if header is None:
                header = row
                continue
            data.append(row)
    return header, data


def write_csv(data, location):
    with open(location, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
    print("Wrote {}".format(location))


def tokenize_idiom(phrase):
    return 'ID' + re.sub(r'[\s|-]', '', phrase).lower() + 'ID'


def remove_punctuation(s):
    return s.translate(str.maketrans('', '', string.punctuation))