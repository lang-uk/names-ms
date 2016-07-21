import os.path
import gc
from hashlib import sha1
from itertools import chain
import msgpack
from dawg import BytesDAWG


NAMES_DAWG = BytesDAWG().load(
    os.path.join(os.path.dirname(__file__), 'dict.dawg'))


def batch_request(names):
    """
    Map all name fragments in the array to name hashes.

    Takes an array of arrays (names are tokenized) and returns
    hashes and labels from DAWG
    """

    def resolve_chunk(prefix):
        def unpack(key, payload):
            return (
                str(key).split("|"),
                msgpack.loads(payload, use_list=False)
            )

        hashes = chain(
            *map(
                lambda key: map(lambda payload: unpack(key, payload),
                                NAMES_DAWG.__getitem__(key)),
                frozenset(NAMES_DAWG.iterkeys(prefix + "|"))
            )
        )

        if hashes:
            return tuple(map(dict, set(
                (
                    ("term", term),
                    ("label", lemma_type),
                    ("lemma", x[b"lemma"])
                )
                for (term, lemma_type), x in hashes
            )))
        else:
            return (({
                "lemma": sha1((prefix + "thisissalt").encode('utf-8')).hexdigest(),
                "label": "no-match",
                "term": prefix
            }, ))

    results = []
    gc.disable()
    for name in names:
        results.append(
            tuple(map(lambda x: resolve_chunk(x), name))
        )
    gc.enable()

    return results
