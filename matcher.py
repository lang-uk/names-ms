from itertools import product, islice
from collections import defaultdict


class Matcher(object):
    def __init__(self, examples=None):
        self.seed = defaultdict(list)

        if examples is not None:
            self.add_examples(examples)

    def filter_and_embellish(self, lemmas):
        # TODO: filtering, processing of unknown entries,
        # double names/lastnames

        # islice(1000) is our safety valve against combinatoric explosion
        for hashes in islice(product(*lemmas), 1000):
            # Very naive generation of variants for now
            yield frozenset(x["lemma"] for x in hashes)

    def add_example(self, id_, example):
        for hashes in self.filter_and_embellish(example):
            self.seed[hashes].append(id_)

    def add_examples(self, examples):
        for id_, example in examples.items():
            self.add_example(id_, example)

    def match(self, candidate):
        for hashes in self.filter_and_embellish(candidate):
            if hashes in self.seed:
                return self.seed[hashes]

        return None
