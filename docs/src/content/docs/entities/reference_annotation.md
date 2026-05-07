---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: ReferenceAnnotation
description: Annotation linking an in-text reference pointer or bibliographic reference to a citation.
---

An annotation that connects an in-text reference pointer or a bibliographic reference to its corresponding [`Citation`](../citation/) entity, optionally characterizing the citation function at that specific textual location. Created via `GraphSet.add_an(resp_agent)`. Short name: `an`. OCDM class: `oa:Annotation`.

## Properties

### body annotation

Functional. RDF predicate: `oa:hasBody`. Accepts: `Citation`.

`has_body_annotation(ci_res)` / `get_body_annotation() -> Citation | None` / `remove_body_annotation()`

The citation entity that this annotation describes.

## Example

```python
g_set = GraphSet("https://w3id.org/oc/meta/")
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

ci = g_set.add_ci(resp_agent)
ci.has_citing_entity(g_set.add_br(resp_agent))
ci.has_cited_entity(g_set.add_br(resp_agent))

an = g_set.add_an(resp_agent)
an.has_body_annotation(ci)

be = g_set.add_be(resp_agent)
be.has_annotation(an)
```
