---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: BibliographicReference
description: Textual reference entry in a resource's reference list.
---

A bibliographic reference is the textual entry in a reference list that points to another resource. It stores the raw reference text and links it to the cited [`BibliographicResource`](../bibliographic_resource/). Created via `GraphSet.add_be(resp_agent)`. Short name: `be`. OCDM class: `biro:BibliographicReference`.

## Properties

### content

Functional. RDF predicate: `c4o:hasContent`.

`has_content(string: str)` / `get_content() -> str | None` / `remove_content()`

The literal text of the reference as it appears in the citing resource, including any errors or formatting choices of the original publisher.

### annotations

Non-functional. RDF predicate: `oco:hasAnnotation`. Accepts: `ReferenceAnnotation`.

`has_annotation(an_res)` / `get_annotations() -> list[ReferenceAnnotation]` / `remove_annotation(an_res=None)`

### referenced resource

Functional. RDF predicate: `biro:references`. Accepts: `BibliographicResource`.

`references_br(br_res)` / `get_referenced_br() -> BibliographicResource | None` / `remove_referenced_br()`

The bibliographic resource that this reference cites.

## Example

```python
g_set = GraphSet("https://w3id.org/oc/meta/")
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

cited = g_set.add_br(resp_agent)
cited.has_title("Software review: COCI")

be = g_set.add_be(resp_agent)
be.has_content("Heibi, I., Peroni, S., & Shotton, D. (2019). Software review: COCI, the OpenCitations Index of Crossref open DOI-to-DOI citations. Scientometrics, 121, 1213-1228.")
be.references_br(cited)

article = g_set.add_br(resp_agent)
article.contains_in_reference_list(be)
```
