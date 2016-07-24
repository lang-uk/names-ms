from itertools import product, islice
from operator import itemgetter
from collections import defaultdict


class Matcher(object):
    # Schemes:
    # Len > 0
    # Firstname
    # Patronymic
    # Lastname
    # Unknown
    # Len > 1
    # Firstname Lastname
    # Firstname Unknown
    # Unknown Lastname
    # Unknown Patronymic
    # Unknown Unknown
    # Firstname Firstname  ; Rare
    # Firstname Patronymic ; Medium Rare
    # Len > 2
    # Fistname Patronymic Lastname
    # Firstname Firstname Lastname ; Rare
    # Firstname Lastname Lastname  ; Rare
    # Firstname Firstname Patronymic ; Super Rare
    # Len > 3
    # Firstname Firtsname Patronymic Lastname ; Rare
    # Firstname Patronymic Lastname Lastname  ; Rare
    # Firstname Firstname Lastname Lastname   ; Super Rare
    # Firstname Firstname Firstname Lastname  ; Super Rare
    # Firstname Lastname Lastname Lastname    ; Super Rare
    # Len > 4
    # Firstname Firstname Patronymic Lastname Lastname ; Super rare
    # Firstname Firstname Firstname Lastname Lastname ; Mega rare
    # Firstname Firstname Lastname Lastname Lastname  ; Mega rare

    def __init__(self, examples=None):
        self.seed = defaultdict(list)

        if examples is not None:
            self.add_examples(examples)

    def generate_by_schema(self, by_type, schema):
        return product(*(by_type[x] for x in schema))

    def generate(self, lemmas):
        def prune_degenerates(candidate):
            positions = frozenset(map(itemgetter(0), candidate))
            if len(positions) != len(candidate):
                return None
            else:
                return tuple(map(itemgetter(1), candidate))

        by_type = self.group_by_type(lemmas)
        lemmas_len = len(lemmas)

        if lemmas_len > 0:
            for t in by_type.keys():
                for _, x in by_type[t]:
                    yield x

        if lemmas_len > 1:
            for x in filter(
                    None, map(prune_degenerates, self.generate_by_schema(by_type, ["f", "l"]))):
                yield x

    def group_by_type(self, lemmas):
        by_type = defaultdict(list)

        for i, lemma in enumerate(lemmas):
            for lemma_variant in lemma:
                by_type[lemma_variant["label"]].append((i, lemma_variant))

        return by_type

    def filter_and_embellish(self, lemmas):
        # TODO: filtering, processing of unknown entries,
        # double names/lastnames

        # islice(1000) is our safety valve against combinatoric explosion
        for hashes in islice(product(*lemmas), 10000000):
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
