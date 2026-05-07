---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: AgentRole
description: A role held by an agent with respect to a bibliographic resource.
---

Links a [`ResponsibleAgent`](../responsible_agent/) to a [`BibliographicResource`](../bibliographic_resource/) through a specific role (author, editor, publisher). Created via `GraphSet.add_ar(resp_agent)`. Short name: `ar`. OCDM class: `pro:RoleInTime`.

## Properties

### next

Functional. RDF predicate: `oco:hasNext`. Accepts: `AgentRole`.

`has_next(ar_res)` / `get_next() -> AgentRole | None` / `remove_next()`

Points to the next role in a sequence. Used to define ordered lists of contributors (e.g. first author, second author).

### is held by

Functional. RDF predicate: `pro:isHeldBy`. Accepts: `ResponsibleAgent`.

`is_held_by(ra_res)` / `get_is_held_by() -> ResponsibleAgent | None` / `remove_is_held_by()`

### role type

Functional. RDF predicate: `pro:withRole`.

`get_role_type() -> str | None` / `remove_role_type()`

Set via one of the role creation methods:

| Method | RDF value |
|---|---|
| `create_author()` | `pro:author` |
| `create_editor()` | `pro:editor` |
| `create_publisher()` | `pro:publisher` |

## Example

```python
g_set = GraphSet("https://w3id.org/oc/meta/")
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

article = g_set.add_br(resp_agent)
article.has_title("OpenCitations Meta")

ra_1 = g_set.add_ra(resp_agent)
ra_1.has_given_name("Arcangelo")
ra_1.has_family_name("Massari")

ra_2 = g_set.add_ra(resp_agent)
ra_2.has_given_name("Silvio")
ra_2.has_family_name("Peroni")

ar_1 = g_set.add_ar(resp_agent)
ar_1.is_held_by(ra_1)
ar_1.create_author()
article.has_contributor(ar_1)

ar_2 = g_set.add_ar(resp_agent)
ar_2.is_held_by(ra_2)
ar_2.create_author()
article.has_contributor(ar_2)

ar_1.has_next(ar_2)
```
