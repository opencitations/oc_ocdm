---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: ResourceEmbodiment
description: Physical or digital manifestation of a bibliographic resource.
---

The specific format in which a bibliographic resource was published: a PDF, an HTML page, a print edition. Created via `GraphSet.add_re(resp_agent)`. Short name: `re`. OCDM class: `fabio:Manifestation`.

## Properties

### media type

Functional. RDF predicate: `dcterms:format`. Values are URI strings.

`has_media_type(thing_res: str)` / `get_media_type() -> str | None` / `remove_media_type()`

An IANA media type URI (e.g. `http://purl.org/NET/mediatypes/application/pdf`).

### starting page

Functional. RDF predicate: `prism:startingPage`.

`has_starting_page(string: str)` / `get_starting_page() -> str | None` / `remove_starting_page()`

If the input contains a dash (e.g. `"22-45"`), everything from the dash onward is stripped, keeping only `"22"`.

### ending page

Functional. RDF predicate: `prism:endingPage`.

`has_ending_page(string: str)` / `get_ending_page() -> str | None` / `remove_ending_page()`

If the input contains a dash (e.g. `"22-45"`), everything before and including the dash is stripped, keeping only `"45"`.

### URL

Functional. RDF predicate: `frbr:exemplar`. Values are URI strings.

`has_url(thing_res: str)` / `get_url() -> str | None` / `remove_url()`

Where this embodiment can be accessed.

## Type classification

| Method | RDF type |
|---|---|
| `create_digital_embodiment()` | `fabio:DigitalManifestation` |
| `create_print_embodiment()` | `fabio:PrintObject` |

## Example

```python
g_set = GraphSet("https://w3id.org/oc/meta/")
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

re = g_set.add_re(resp_agent)
re.create_digital_embodiment()
re.has_media_type("http://purl.org/NET/mediatypes/application/pdf")
re.has_url("https://direct.mit.edu/qss/article-pdf/5/1/50/2373930/qss_a_00292.pdf")
re.has_starting_page("50")
re.has_ending_page("75")

article = g_set.add_br(resp_agent)
article.has_format(re)
```
