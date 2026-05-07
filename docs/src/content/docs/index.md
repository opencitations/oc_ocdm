---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: Quick start
description: Install oc-ocdm and create your first bibliographic entity.
---

oc-ocdm is a Python library for producing, modifying and exporting RDF data structures compliant with the [OCDM specification](https://figshare.com/articles/Metadata_for_the_OpenCitations_Corpus/3443876). It requires Python 3.10 or later.

```
pip install oc-ocdm
```

Create a bibliographic resource, assign it a title and a DOI, then write the result to a JSON-LD file:

```python
from oc_ocdm.graph import GraphSet
from oc_ocdm import Storer

base_iri = "https://w3id.org/oc/meta/"
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

g_set = GraphSet(base_iri)
br = g_set.add_br(resp_agent)
br.has_title("OpenCitations Meta")
br.create_journal_article()
br.has_pub_date("2024-03")

doi = g_set.add_id(resp_agent)
doi.create_doi("10.1162/qss_a_00292")
br.has_identifier(doi)

storer = Storer(g_set)
storer.store_graphs_in_file("output.jsonld")
```

This produces a JSON-LD file containing the RDF triples for the resource and its identifier.

## Next steps

- [GraphSet](./guides/graph_set/): create and manage graph entities
- [Entities](./entities/bibliographic_resource/): entity types and all their methods
- [Metadata](./guides/metadata/): datasets and distributions
- [Reading data](./guides/reading/): import entities from RDF files or SPARQL endpoints
- [Storing data](./guides/storing/): persist changes to files or triplestores
- [Provenance](./guides/provenance/): track entity history with provenance snapshots
- [Counter handlers](./guides/counter_handlers/): strategies for generating unique entity IRIs
