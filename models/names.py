from elasticsearch_dsl import DocType, String, Object, document
from elasticsearch_dsl.query import Match
from elasticsearch_dsl import MultiSearch
from hashlib import sha1


def whitelist(dct, fields):
    """
    Leave only those fields which keys are present in `fields`.

    :param dct: Source dictionary
    :type dct: dict
    :param fields: List of fields to keep
    :type fields: list
    :return: Resulting dictionary containing whitelisted fields only
    :rtype: dict
    """
    return {
        k: v for k, v in dct.items() if k in fields
    }


class NameVariant(DocType):
    labels = String(
        index="not_analyzed",
    )
    lemma = String(
        index="not_analyzed",
    )
    lemma_labels = String(
        index="not_analyzed",
    )
    term = String(
        index="not_analyzed",
    )

    properties = Object()

    @classmethod
    def batch_request(cls, names):
        """
        Map all name fragments in the array to name hashes.

        Takes an array of arrays (names are tokenized) and returns
        hashes and labels from ES.
        """
        # TODO: THROW IT AWAY AND REPLACE WITH DAWG
        def search_clause(term):
            # TODO: case for initials
            return cls.search().filter("term", term=term)

        def transform_resp(resp):
            labels = list(set(resp.lemma_labels) - {"lemma"})
            assert len(labels) == 1

            label = {
                "lemma-firstname": "firstname",
                "lemma-patronymic": "patronymic",
                "lemma-lastname": "lastname",
                "lemma-firstname-typo": "firstname",
                "lemma-patronymic-typo": "patronymic",
                "lemma-lastname-typo": "lastname"
            }[labels[0]]

            return {
                "term": resp.term,
                "lemma": resp.lemma,
                "label": label
            }

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

        qs = MultiSearch(index=cls._doc_type.index)
        for name in names:
            for chunk in name:
                qs = qs.add(search_clause(chunk))

        response = qs.execute()
        results = []

        pos = 0
        for name in names:
            l = len(name)

            res_chunk = match_req_resp(name, response[pos:pos + l])

            results.append(res_chunk)
            pos += l

        return results

    class Meta:
        index = "names",
        include_in_all = False
        dynamic_templates = document.MetaField([
            {
                "stored_properties_template": {
                    "path_match": "properties.*",
                    "mapping": {
                        "store": "yes",
                        "index": "no"
                    }
                }
            }
        ])
