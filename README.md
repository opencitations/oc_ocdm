<!--
SPDX-FileCopyrightText: 2020-2023 Simone Persiani <iosonopersia@gmail.com>
SPDX-FileCopyrightText: 2022-2025 Arcangelo Massari <arcangelo.massari@unibo.it>

SPDX-License-Identifier: ISC
-->

# oc_ocdm
[<img src="https://img.shields.io/badge/powered%20by-OpenCitations-%239931FC?labelColor=2D22DE" />](http://opencitations.net)
[![Run tests](https://github.com/opencitations/oc_ocdm/actions/workflows/run_tests.yml/badge.svg)](https://github.com/opencitations/oc_ocdm/actions/workflows/run_tests.yml)
[![Coverage](https://opencitations.github.io/oc_ocdm/coverage/coverage-badge.svg)](https://opencitations.github.io/oc_ocdm/coverage/)
[![Documentation](https://img.shields.io/badge/docs-Starlight-blue)](https://opencitations.github.io/oc_ocdm/)
[![REUSE](https://github.com/opencitations/oc_ocdm/actions/workflows/reuse.yml/badge.svg)](https://github.com/opencitations/oc_ocdm/actions/workflows/reuse.yml)
[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg)](https://opensource.org/licenses/ISC)
[![PyPI version](https://badge.fury.io/py/oc-ocdm.svg)](https://badge.fury.io/py/oc-ocdm)
[![DOI](https://zenodo.org/badge/322327342.svg)](https://zenodo.org/badge/latestdoi/322327342)

Python library for creating, manipulating, and exporting RDF data compliant with the [OpenCitations Data Model](https://figshare.com/articles/Metadata_for_the_OpenCitations_Corpus/3443876). It handles OCDM entities (bibliographic resources, agents, identifiers, etc.) without requiring direct knowledge of RDF or SPARQL.

## Quick start

```bash
pip install oc_ocdm
```

```python
from oc_ocdm.graph import GraphSet
from oc_ocdm import Storer

g_set = GraphSet("https://w3id.org/oc/meta/")
br = g_set.add_br("https://w3id.org/oc/meta/prov/pa/1")
br.has_title("OpenCitations Meta")
br.create_journal_article()

doi = g_set.add_id("https://w3id.org/oc/meta/prov/pa/1")
doi.create_doi("10.1162/qss_a_00292")
br.has_identifier(doi)

storer = Storer(g_set)
storer.store_graphs_in_file("output.jsonld")
```

For guides, API reference, and examples, see the [documentation](https://opencitations.github.io/oc_ocdm/).
