---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: PointerList
description: Group of in-text reference pointers appearing together in the text.
---

A textual device that groups multiple reference pointers at a single location in the text (e.g. `[1, 2, 3]` or `[4-9]`). Created via `GraphSet.add_pl(resp_agent)`. Short name: `pl`. OCDM class: `c4o:SingleLocationPointerList`.

## Properties

### content

Functional. RDF predicate: `c4o:hasContent`.

`has_content(string: str)` / `get_content() -> str | None` / `remove_content()`

The literal text of the pointer list as it appears in the document (e.g. `"[1, 2, 3]"`).

### contained elements

Non-functional. RDF predicate: `co:element`. Accepts: `ReferencePointer`.

`contains_element(rp_res)` / `get_contained_elements() -> list[ReferencePointer]` / `remove_contained_element(rp_res=None)`

The individual reference pointers that make up this list.

## Example

```python
g_set = GraphSet("https://w3id.org/oc/meta/")
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

rp_1 = g_set.add_rp(resp_agent)
rp_1.has_content("[1]")
rp_2 = g_set.add_rp(resp_agent)
rp_2.has_content("[2]")
rp_1.has_next_rp(rp_2)

pl = g_set.add_pl(resp_agent)
pl.has_content("[1, 2]")
pl.contains_element(rp_1)
pl.contains_element(rp_2)

paragraph = g_set.add_de(resp_agent)
paragraph.create_paragraph()
paragraph.is_context_of_pl(pl)
```
