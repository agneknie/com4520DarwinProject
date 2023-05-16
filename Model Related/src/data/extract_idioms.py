from data.util import load_csv

"""
Create a list of all MWEs in the given datasets

Parameters:
    data_path : str
        The path to the directory containing the default SubtaskB datasets. E.g. data/datasets/SemEval_2022_Task2_SubTaskB/.
    languages : list[str]
        List of languages to include. Default is ['EN', 'PT']

Returns:
    idioms : list[str]
        A list of MWEs contained in the given datasets
"""
def extract_idioms(data_path, languages=['EN', 'PT']):
    idioms = []
    for data_split in ['/TrainData/train_data.csv', '/EvaluationData/dev.csv', '/EvaluationData/eval.csv']:
        header, data = load_csv(data_path + data_split)
        for elem in data:
            if elem[header.index('Language')] not in languages:
                continue
            idioms.append(elem[header.index('MWE1')])
            idioms.append(elem[header.index('MWE2')])

    idioms = list( set( idioms ) ) 
    idioms.remove( 'None' ) 

    return idioms