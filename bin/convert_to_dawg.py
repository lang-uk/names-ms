import sys
import msgpack
import dawg
import os.path
from ujson import loads
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from name_utils import normalize_charset


def add_to_dct(x, dct):
    return dct.setdefault(x, len(dct))


def get_lemma_type(rec):
    labels = list(set(rec["lemma_labels"]) - {"lemma"})
    assert len(labels) == 1

    return {
        "lemma-firstname": "firstname",
        "lemma-patronymic": "patronymic",
        "lemma-lastname": "lastname",
        "lemma-firstname-typo": "firstname",
        "lemma-patronymic-typo": "patronymic",
        "lemma-lastname-typo": "lastname"
    }[labels[0]]


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception("Input file argument is not specified")

    input_fname = sys.argv[1]
    if not os.path.exists(input_fname):
        raise Exception("Input file doesn't exist")

    lemmas = {}
    labels = {}
    dictionary = []

    with open(input_fname, encoding="utf-8") as input_fp:
        for i, line in enumerate(input_fp):
            rec = loads(line)
            term = normalize_charset(rec["term"])
            rec["lemma"] = add_to_dct(rec["lemma"], lemmas)

            lemma_type = get_lemma_type(rec)
            del rec["properties"]
            del rec["lemma_labels"]
            del rec["term"]
            rec["labels"] = list(
                map(
                    lambda x: add_to_dct(x, labels),
                    rec["labels"]))

            dictionary.append(
                ("%s|%s" % (term, lemma_type), msgpack.packb(rec))
            )

            if i and i % 100000 == 0:
                print("%s records processed" % i)

    packed_dict = dawg.BytesDAWG(dictionary)
    packed_dict.save("dict.dawg")

    with open("lemma_dict.mpack", "wb") as fp:
        msgpack.dump(lemmas, fp)

    with open("label_dict.mpack", "wb") as fp:
        msgpack.dump(labels, fp)
