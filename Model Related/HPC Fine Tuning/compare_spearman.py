"""
This is a script to easily plot and compare the spearman ranks over epochs of multiple models

Usage:
python compare_spearman.py <path to repo> <result type> <model path 1> <model path 2> <model path 3> ...

<path to repo>: the path to the com4520DarwinProject folder on your pc. If you are calling this script 
                from the repo root you can just use . 
                this allows you to copy this script to anywhere on your pc (e.g. in a folder containing all models you wish to compare)
<result type>: One of [ALL, "Idiom Data", "STS Data"]
<model path X>: The path to a trained model on your pc. Assumes that the eval subfolder is filled with results from training
"""
import sys
import os
import matplotlib.pyplot as plt


if __name__ == '__main__':
    if len(sys.argv) < 4:
        raise Exception('Must at least supply the path to the com4520DarwinProject dir, the result type and a model path')
    repo_path = sys.argv[1]
    result_type = sys.argv[2]
    model_paths = sys.argv[3:]

    sys.path.append(os.path.join(repo_path, 'src'))
    from visualisation.plot import plot_spearman_epochs

    for model_path in model_paths:
        plot_spearman_epochs(model_path, 'Spearman Rank ' + result_type, languages=['EN'], label=model_path)

    plt.title('Spearman Rank ' + result_type)
    plt.legend()
    plt.show()

