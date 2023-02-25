import os
from sentence_transformers.evaluation import SentenceEvaluator
from scipy.stats import pearsonr, spearmanr
from evaluation.get_similarities import get_dataset_similarities
from data.idiom_dataset import load_dataset, IdiomDataset
from data.util import load_csv, write_csv

class IdiomEvaluator(SentenceEvaluator):
    def __init__(self, dev_eval_path, save_path=None, tokenize_idioms=False, transform=None, languages=['EN', 'PT']):
        self.header, self.data = load_dataset(os.path.join(dev_eval_path, 'dev.csv'), tokenize_idioms=tokenize_idioms, transform=transform, languages=languages)
        self.dataset = IdiomDataset(self.header, self.data ,languages=languages)
        
        self.gold_header, self.gold_data = load_csv(os.path.join(dev_eval_path, 'dev.gold.csv'))
        self.save_path = save_path
        self.languages = languages

    def __call__(self, model, output_path, epoch, steps):
        sims = get_dataset_similarities(self.dataset, model)

        sims_dict = {}
        for (elem, sim) in zip(self.data, sims):
            sims_dict[elem[self.header.index('ID')]] = sim

        # same logic as SubTask2Evaluator.py `_score` function
        gold_labels_all = []
        predictions_all = []

        gold_labels_sts = []
        predictions_sts = []

        gold_labels_no_sts = []
        predictions_no_sts = []

        for elem in self.gold_data :
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

        if self.save_path is not None:
            sims_data = [['ID', 'Language', 'Setting', 'Sim']]
            for (elem, sim) in zip(self.data, sims):
                sims_data.append([
                    elem[self.header.index('ID')], elem[self.header.index('Language')], 'fine_tune', sim
                ])
            write_csv(sims_data, os.path.join(self.save_path, f'sims_{epoch}.csv'))

            results_data = [
                ['Settings', 'Languages', 'Spearman Rank ALL', 'Spearman Rank Idiom Data', 'Spearman Rank STS Data'],
                ['fine_tune', ','.join(self.languages), corel_all, corel_no_sts, corel_sts]
                ]
            write_csv(results_data, os.path.join(self.save_path, f'results_{epoch}.csv'))

        return corel_all
