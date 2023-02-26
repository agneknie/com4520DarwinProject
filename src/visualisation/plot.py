import matplotlib.pyplot as plt
import os
from data.util import load_csv


def plot_spearman_epochs(model_path, column, settings=['fine_tune'], languages=['EN', 'PT'], **kwargs):
    files = os.listdir(os.path.join(model_path, 'eval'))
    n_epochs = len([file for file in files if file[:7] == 'results'])
    scores = []
    settings = ['fine_tune']
    for i in range(n_epochs):
        header, results = load_csv(os.path.join(model_path, 'eval', f'results_{i}.csv'))
        for row in results:
            if row[header.index('Settings')] == settings[0] and row[header.index('Languages')] == ','.join(languages):
                scores.append(float(row[header.index(column)]))

    plt.plot(range(1, len(scores)+1), scores, label=column, **kwargs)
    plt.xlabel('Epochs')
    plt.ylabel('Spearman Rank')
    plt.xticks(range(1, len(scores)+1))
