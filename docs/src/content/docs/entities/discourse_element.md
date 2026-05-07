---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: DiscourseElement
description: Structural or rhetorical component of a document.
---

A part of a document's structure: a section, paragraph, sentence, table, footnote, or a rhetorical unit like an introduction or conclusion. Discourse elements can be nested and ordered. Created via `GraphSet.add_de(resp_agent)`. Short name: `de`. OCDM class: `deo:DiscourseElement`.

## Properties

### title

Functional. RDF predicate: `dcterms:title`.

`has_title(string: str)` / `get_title() -> str | None` / `remove_title()`

### contained discourse elements

Non-functional. RDF predicate: `frbr:part`. Accepts: `DiscourseElement`.

`contains_discourse_element(de_res)` / `get_contained_discourse_elements() -> list[DiscourseElement]` / `remove_contained_discourse_element(de_res=None)`

Nested children: a section contains paragraphs, a paragraph contains sentences.

### next discourse element

Functional. RDF predicate: `oco:hasNext`. Accepts: `DiscourseElement`.

`has_next_de(de_res)` / `get_next_de() -> DiscourseElement | None` / `remove_next_de()`

Ordering among sibling elements at the same nesting level.

### context of reference pointers

Non-functional. RDF predicate: `c4o:isContextOf`. Accepts: `ReferencePointer`.

`is_context_of_rp(rp_res)` / `get_is_context_of_rp() -> list[ReferencePointer]` / `remove_is_context_of_rp(rp_res=None)`

The in-text reference pointers that appear within this discourse element.

### context of pointer lists

Non-functional. RDF predicate: `c4o:isContextOf`. Accepts: `PointerList`.

`is_context_of_pl(pl_res)` / `get_is_context_of_pl() -> list[PointerList]` / `remove_is_context_of_pl(pl_res=None)`

### content

Functional. RDF predicate: `c4o:hasContent`.

`has_content(string: str)` / `get_content() -> str | None` / `remove_content()`

The literal text of this discourse element.

### number

Functional. RDF predicate: `fabio:hasSequenceIdentifier`.

`has_number(string: str)` / `get_number() -> str | None` / `remove_number()`

## Type classification

Discourse elements carry two kinds of type: structural and rhetorical. They behave differently.

### Structural types (replace existing secondary type)

These work like type methods on other entities: each call replaces the previous secondary `rdf:type`.

| Method | RDF type |
|---|---|
| `create_discourse_element(de_class=None)` | `deo:DiscourseElement` (or custom IRI via `de_class`) |
| `create_section()` | `doco:Section` |
| `create_section_title()` | `doco:SectionTitle` |
| `create_paragraph()` | `doco:Paragraph` |
| `create_sentence()` | `doco:Sentence` |
| `create_text_chunk()` | `doco:TextChunk` |
| `create_table()` | `doco:Table` |
| `create_footnote()` | `doco:Footnote` |
| `create_caption()` | `deo:Caption` |

### Rhetorical types (additive)

These are **not** mutually exclusive. Calling `create_introduction()` does not remove an existing structural type; it adds a new `rdf:type` triple. A single discourse element can combine a structural type (e.g. `doco:Section`) with one or more rhetorical types (e.g. `deo:Introduction`).

| Method | RDF type |
|---|---|
| `create_introduction()` | `deo:Introduction` |
| `create_methods()` | `deo:Methods` |
| `create_materials()` | `deo:Materials` |
| `create_related_work()` | `deo:RelatedWork` |
| `create_results()` | `deo:Results` |
| `create_discussion()` | `deo:Discussion` |
| `create_conclusion()` | `deo:Conclusion` |

## Example

```python
g_set = GraphSet("https://w3id.org/oc/meta/")
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

intro = g_set.add_de(resp_agent)
intro.create_section()
intro.create_introduction()
intro.has_title("Introduction")
intro.has_number("1")

methods = g_set.add_de(resp_agent)
methods.create_section()
methods.create_methods()
methods.has_title("Methods")
methods.has_number("2")
intro.has_next_de(methods)

para = g_set.add_de(resp_agent)
para.create_paragraph()
intro.contains_discourse_element(para)

article = g_set.add_br(resp_agent)
article.contains_discourse_element(intro)
article.contains_discourse_element(methods)
```
