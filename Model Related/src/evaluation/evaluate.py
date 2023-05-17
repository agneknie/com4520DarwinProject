import os
import pandas as pd
from data.idiom_dataset import IdiomDataset, load_dataset
from data.util import load_csv, write_csv
from evaluation.SubTask2Evaluator import evaluate_submission
from evaluation.get_similarities import get_dataset_similarities


"""
Create a list of similarity data that matches the submission format.
(Doesn't write anything to a file)

Parameters:
    languages : list[str]
        Languages to include.
    settings : list[str]
        A list containing either 'pre_train' or 'fine_tune' depending on which subtask setting the model is for.
    sims : list[float]
        A list of similarities.
    location : str
        The location of the given submission format csv file.

Returns
    [header] + data : list
        The csv data in a list.
"""
def insert_to_submission( languages, settings, sims, location ) : 
    header, data = load_csv( location ) 
    sims = list( reversed( sims ) )
    ## Validate with length
    updatable = [ i for i in data if i[ header.index( 'Language' ) ] in languages and i[ header.index( 'Setting' ) ] in settings ]
    assert len( updatable ) == len( sims ) 

    ## Will update in sequence - if data is not in sequence must update one language / setting at a time. 
    started_update = False
    for elem in data : 
        if elem[ header.index( 'Language' ) ] in languages and elem[ header.index( 'Setting' ) ] in settings : 
            sim_to_insert = sims.pop()
            elem[-1] = sim_to_insert
            started_update = True
        else:  
            assert not started_update ## Once we start, we must complete. 
        if len( sims ) == 0 : 
            break 
    assert len( sims ) == 0 ## Should be done here. 

    return [ header ] + data ## Submission file must retain header. 


"""
Evaluate a model on the dev set

Parameters:
    model : SentenceTransformer
        The model
    data_path : str
        The path to the directory containing the default evaluation SubtaskB datasets. 
        E.g. data/datasets/SemEval_2022_Task2_SubTaskB/EvaluationData
    results_file : str
        The file to write the results to
    settings : list[str]
        A list containing either 'pre_train' or 'fine_tune' depending on which subtask setting the model is for.
    languages : list[str]
        List of languages to include. Default is ['EN', 'PT']
    tokenize_idioms : bool
        Whether to use a single token for each MWE. Default is False.
    transform : (list[str], list[str]) -> list[str]
        Takes a list of sentences and corresponding MWEs, should return a transformed list of sentences 

Returns:
    results : TODO
"""
def get_dev_results(model, data_path, results_file, settings, languages=['EN', 'PT'], tokenize_idioms=False, transform=None):
    header, data = load_dataset(os.path.join(data_path, 'dev.csv'), tokenize_idioms=tokenize_idioms, transform=transform, languages=languages)
    dataset = IdiomDataset(header, data ,languages=languages)
    
    print('First dev sample: ', 
        ' '.join(model.tokenizer.tokenize(dataset[0].texts[0])), '\n',
        ' '.join(model.tokenizer.tokenize(dataset[0].texts[1])))
    print('Num dev samples: ', len(dataset))
    sims = get_dataset_similarities(dataset, model)

    ## Create submission file on the development set. 
    submission_data = insert_to_submission(languages, settings, sims, os.path.join(data_path, 'dev.submission_format.csv'))
    write_csv(submission_data, results_file)

    results = evaluate_submission(results_file, os.path.join(data_path, 'dev.gold.csv'))
    return results


"""
Save the similarity score on the eval set in the submission format.

Parameters:
    model : SentenceTransformer
        The model
    data_path : str
        The path to the directory containing the default evaluation SubtaskB datasets. 
        E.g. data/datasets/SemEval_2022_Task2_SubTaskB/EvaluationData
    results_file : str
        The file to write the results to
    settings : list[str]
        A list containing either 'pre-train' or 'fine-tune' depending on which subtask setting the model is for.
    languages : list[str]
        List of languages to include. Default is ['EN', 'PT']
    tokenize_idioms : bool
        Whether to use a single token for each MWE. Default is False.
    transform : (list[str], list[str]) -> list[str]
        Takes a list of sentences and corresponding MWEs, should return a transformed list of sentences 
"""
def save_eval_output(model, data_path, results_file, settings, languages=['EN', 'PT'], tokenize_idioms=False, transform=None):
    header, data = load_dataset(os.path.join(data_path, 'eval.csv'), tokenize_idioms=tokenize_idioms, transform=transform, languages=languages)
    dataset = IdiomDataset(header, data, languages=languages)
    print('First eval sample: ', 
        ' '.join(model.tokenizer.tokenize(dataset[0].texts[0])), '\n',
        ' '.join(model.tokenizer.tokenize(dataset[0].texts[1])))
    print('Num eval samples: ', len(dataset))
    sims = get_dataset_similarities(dataset, model)

    submission_data = insert_to_submission(languages, settings, sims, os.path.join(data_path, 'eval.submission_format.csv'))  
    write_csv(submission_data, results_file)
    

"""
Format results to be printed

Parameters:
    results : TODO

Returns
    Dataframe containing the results
"""
def format_results(results):
    for result in results : 
        for result_index in range( 2, 5 ) : 
            result[result_index] = 'Did Not Attempt' if result[result_index] is None else result[ result_index ]
    return pd.DataFrame(data=results[1:], columns=results[0])