import os
from sentence_transformers.evaluation import SentenceEvaluator
from scipy.stats import pearsonr, spearmanr
from evaluation.get_similarities import get_dataset_similarities
from data.idiom_dataset import load_dataset, IdiomDataset
from data.util import load_csv, write_csv


"""
Evaluator using the spearman rank, calculated in the same way as SubTask2Evaluator.py

Parameters
    dev_eval_path : str
        Path to the directory containing dev and eval datasets
    save_path : str
        Path to directory to save results files at. Default is None.
    tokenize_idioms : bool
        Whether to use a single token for each MWE. Default is False.
    languages : list[str]
        List of languages to include. Default is ['EN', 'PT']
    transform : (list[str], list[str]) -> list[str]
        Takes a list of sentences and corresponding MWEs, should return a transformed list of sentences 
"""
class IdiomEvaluator(SentenceEvaluator):
    def __init__(self, dev_eval_path, save_path=None, tokenize_idioms=False, transform=None, languages=['EN', 'PT']):
        self.header, self.data = load_dataset(os.path.join(dev_eval_path, 'dev.csv'), tokenize_idioms=tokenize_idioms, transform=transform, languages=languages)
        self.dataset = IdiomDataset(self.header, self.data ,languages=languages)
        
        self.gold_header, self.gold_data = load_csv(os.path.join(dev_eval_path, 'dev.gold.csv'))
        self.save_path = save_path
        self.languages = languages

    def __call__(self, model, output_path, epoch, steps):
        sims = get_dataset_similarities(self.dataset, model)
        results_data = [
                ['Settings', 'Languages', 'Spearman Rank ALL', 'Spearman Rank Idiom Data', 'Spearman Rank STS Data']
                ]
        for languages in [[lang] for lang in self.languages] + ([self.languages] if len(self.languages) > 1 else []):

            sims_dict = {}
            for (elem, sim) in zip(self.data, sims):
                if elem[self.header.index('Language')] in languages:
                    sims_dict[elem[self.header.index('ID')]] = sim

            # same logic as SubTask2Evaluator.py `_score` function
            gold_labels_all = []
            predictions_all = []

            gold_labels_sts = []
            predictions_sts = []

            gold_labels_no_sts = []
            predictions_no_sts = []

            for elem in self.gold_data :
                if elem[self.gold_header.index('Language')] not in languages:
                    continue
                this_sim = elem[ self.gold_header.index( 'sim' ) ]
                if this_sim == '' : 
                    this_sim = sims_dict[ elem[ self.gold_header.index( 'otherID' ) ] ]
                this_sim = float( this_sim )
                this_prediction = float( sims_dict[ elem[ self.gold_header.index( 'ID' ) ] ] )

                gold_labels_all.append( this_sim        )
                predictions_all.append( this_prediction )

                if elem[ self.gold_header.index( 'DataID' ) ].split( '.' )[2] == 'sts' :
                    gold_labels_sts.append( this_sim        )
                    predictions_sts.append( this_prediction )
                else : 
                    gold_labels_no_sts.append( this_sim        )
                    predictions_no_sts.append( this_prediction )

            corel_all, pvalue    =  spearmanr(gold_labels_all   , predictions_all    ) 
            corel_sts, pvalue    =  spearmanr(gold_labels_sts   , predictions_sts    ) 
            corel_no_sts, pvalue =  spearmanr(gold_labels_no_sts, predictions_no_sts ) 

            results_data.append(
                ['fine_tune', ','.join(languages), corel_all, corel_no_sts, corel_sts]
            )

        # in the last iteration languages == self.languages so this is fine
        if self.save_path is not None:
            sims_data = [['ID', 'Language', 'Setting', 'Sim']]
            for (elem, sim) in zip(self.data, sims):
                sims_data.append([
                    elem[self.header.index('ID')], elem[self.header.index('Language')], 'fine_tune', sim
                ])
            write_csv(sims_data, os.path.join(self.save_path, f'sims_{epoch}.csv'))

            write_csv(results_data, os.path.join(self.save_path, f'results_{epoch}.csv'))

        return corel_all
