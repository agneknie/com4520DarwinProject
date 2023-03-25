import matplotlib.pyplot as plt
import os
from data.util import load_csv

"""
Plot spearman rank against epochs trained.
The data for this can be generated during training using the `dev_eval_path` parameter of `fine_tune_model`

Parameters:
    model_path : str
        The path where the model is saved
    column : str
        The data to plot. Must be one of ['Spearman Rank ALL', 'Spearman Rank Idiom Data', 'Spearman Rank STS Data']
    settings : list[str]
        Must be ['fine_tune'] or ['pre_train']. Default is ['fine_tune']
    languages : list[str]
        List of languages to include. Default is ['EN', 'PT']
    **kwargs
        extra arguments to pass on to plt.plot, e.g. color or marker
"""
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

    if 'label' in kwargs:
        label = kwargs['label']
        del kwargs['label']
    else:
        label = column

    plt.plot(range(1, len(scores)+1), scores, label=label, **kwargs)
    plt.xlabel('Epochs')
    plt.ylabel('Spearman Rank')
    plt.xticks(range(1, len(scores)+1))
