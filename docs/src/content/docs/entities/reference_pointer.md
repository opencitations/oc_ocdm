---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: ReferencePointer
description: In-text textual device denoting a single bibliographic reference.
---

A textual device embedded in a document's text (e.g. `[1]`, `(Smith 2020)`) that denotes a single bibliographic reference. Multiple pointers can refer to the same reference, and they can be chained in reading order. Created via `GraphSet.add_rp(resp_agent)`. Short name: `rp`. OCDM class: `c4o:InTextReferencePointer`.

## Properties

### content

Functional. RDF predicate: `c4o:hasContent`.

`has_content(string: str)` / `get_content() -> str | None` / `remove_content()`

The literal text of the pointer as it appears in the document (e.g. `"[1]"`).

### next reference pointer

Functional. RDF predicate: `oco:hasNext`. Accepts: `ReferencePointer`.

`has_next_rp(rp_res)` / `get_next_rp() -> ReferencePointer | None` / `remove_next_rp()`

The next pointer when part of an in-text reference pointer list.

### denoted reference

Functional. RDF predicate: `c4o:denotes`. Accepts: `BibliographicReference`.

`denotes_be(be_res)` / `get_denoted_be() -> BibliographicReference | None` / `remove_denoted_be()`

The bibliographic reference in the reference list that this pointer denotes.

### annotations

Non-functional. RDF predicate: `oco:hasAnnotation`. Accepts: `ReferenceAnnotation`.

`has_annotation(an_res)` / `get_annotations() -> list[ReferenceAnnotation]` / `remove_annotation(an_res=None)`

## Example

```python
g_set = GraphSet("https://w3id.org/oc/meta/")
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

be = g_set.add_be(resp_agent)
be.has_content("Peroni, S. (2020). ...")

rp = g_set.add_rp(resp_agent)
rp.has_content("[1]")
rp.denotes_be(be)

section = g_set.add_de(resp_agent)
section.create_paragraph()
section.is_context_of_rp(rp)
```
