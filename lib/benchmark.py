import inspect
from lib.benchmark_metrics import MRR, basic_metric

class Benchmark:
    def __init__(self):
        self.diseases = set()
        self.compounds = set()
        self.pos_rel = {}
        self.neg_rel = {}
        self.metrics = {}
        # add MRR as default evaluation metric
        self.add_metric('MRR', MRR)

    # n_diseases and n_compounds
    @property
    def n_disease(self):
        return len(self.diseases)

    @property
    def n_compound(self):
        return len(self.compounds)

    # positive and negative relation counts
    @property
    def n_pos_relation(self):
        return sum(len(x) for x in self.pos_rel.values())

    @property
    def n_neg_relation(self):
        return sum(len(x) for x in self.neg_rel.values())
    
    # add dataset
    # Duplicate dataset will be merged
    def add_dataset(self, 
        disease, 
        dataset, 
        drug_id_col=1,
        activity_col=None,
        header=False,
        sep=','
    ):
        drug_id_col -= 1
        if activity_col:
            activity_col -= 1
        with open(dataset) as fr:
            if header:
                fr.readline()
            for l in fr:
                ws = l.rstrip().split(sep)
                if disease not in self.diseases:
                    self.diseases.add(disease)
                    self.pos_rel[disease] = set()
                    self.neg_rel[disease] = set()
                self.compounds.add(ws[drug_id_col])
                # No information for activatity, treat all as positive
                if not activity_col:
                    self.pos_rel[disease].add(ws[drug_id_col])
                # Otherwise, split positive and negative
                else:
                    if int(ws[activity_col]) == 1:
                        self.pos_rel[disease].add(ws[drug_id_col])
                    else:
                        self.neg_rel[disease].add(ws[drug_id_col])

    # add metrics
    def add_metric(self, name, function, **kwargs):
        # check if the function is legal
        parameters = inspect.signature(function).parameters
        required_args = ['predicts', 'positives', 'negatives']
        assert all([x in parameters for x in required_args]), \
            'The input function must have these three args: ' + \
            'predicts, positives, negatives' 
        # add function
        self.metrics[name] = {
            'func':function, 
            'kwargs': kwargs
        }
    
    # evaluate
    def evaluate(self, predicts:dict):
        res = {}
        for metric in self.metrics:
            func = self.metrics[metric]['func']
            kwargs = self.metrics[metric]['kwargs']
            res[metric] = func(
                predicts = predicts,
                positives = self.pos_rel,
                negatives = self.neg_rel,
                **kwargs
            )
        return res
