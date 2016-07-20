import os.path
from hashlib import sha1
from itertools import chain
import msgpack
from dawg_python import BytesDAWG


def batch_request(names):
    """
    Map all name fragments in the array to name hashes.

    Takes an array of arrays (names are tokenized) and returns
    hashes and labels from DAWG
    """
    d = BytesDAWG().load(os.path.join(os.path.dirname(__file__), 'dict.dawg'))

    def transform_resp(resp):
        return resp

        # labels = list(set(resp.lemma_labels) - {"lemma"})
        # assert len(labels) == 1

        # label = {
        #     "lemma-firstname": "firstname",
        #     "lemma-patronymic": "patronymic",
        #     "lemma-lastname": "lastname",
        #     "lemma-firstname-typo": "firstname",
        #     "lemma-patronymic-typo": "patronymic",
        #     "lemma-lastname-typo": "lastname"
        # }[labels[0]]

        # return {
        #     "term": resp.term,
        #     "lemma": resp.lemma,
        #     "label": label
        # }

    def match_req_resp(name, hashes):
        res = []

        for chunk, resp in zip(name, hashes):
            if resp:
                res.append(list(map(transform_resp, resp)))
            else:
                res.append([{
                    "lemma": sha1((chunk + "thisissalt").encode('utf-8')).hexdigest(),
                    "label": "no-match",
                    "term": chunk
                }])
        return res

    def resolve_chunk(prefix):
        return list(chain(
            *map(
                lambda x: map(msgpack.loads, d.__getitem__(x)),
                set(d.keys(prefix))
            )
        ))

    results = []
    for name in names:
        results.append([
            list(map(lambda x: resolve_chunk(x + "|"), name))
        ])

    # pos = 0
    # for name in names:
    #     l = len(name)

    #     res_chunk = match_req_resp(name, response[pos:pos + l])

    #     results.append(res_chunk)
    #     pos += l

    return results
