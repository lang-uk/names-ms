from elasticsearch_dsl import DocType, String, Object, document


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
