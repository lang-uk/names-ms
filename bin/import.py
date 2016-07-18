import sys
import re
import os.path
from json import loads
from elasticsearch_dsl import Index
from elasticsearch.helpers import streaming_bulk
from elasticsearch_dsl.connections import connections
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from models.names import NameVariant
from name_utils import normalize_charset
from settings import ELASTICSEARCH_CONNECTIONS


def bulk_load(docs_to_index):
    conn = connections.get_connection()
    index = NameVariant._doc_type.index

    for response in streaming_bulk(
            conn,
            docs_to_index,
            index=index,
            doc_type=NameVariant._doc_type.name):
        pass


def normalize_alphabet(rec):
    rec["term"] = normalize_charset(rec["term"])
    return rec

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception("Input file argument is not specified")

    input_fname = sys.argv[1]
    if not os.path.exists(input_fname):
        raise Exception("Input file doesn't exist")

    connections.configure(**ELASTICSEARCH_CONNECTIONS)
    Index(NameVariant._doc_type.index).delete(ignore=404)
    NameVariant.init()

    accum = []
    total_lines = 0
    with open(input_fname, encoding="utf-8") as input_fp:
        for i, line in enumerate(input_fp):
            accum.append(loads(line))
            if len(accum) >= 10000:
                total_lines += len(accum)
                bulk_load(map(normalize_alphabet, accum))
                accum = []
                print("Loaded: %s items" % total_lines)

        bulk_load(accum)
