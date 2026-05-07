---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: ResponsibleAgent
description: A person or organization holding a role with respect to a bibliographic resource.
---

An agent (person or organization) that plays a role in relation to a bibliographic resource: author, editor, publisher. Created via `GraphSet.add_ra(resp_agent)`. Short name: `ra`. OCDM class: `foaf:Agent`.

## Properties

### name

Functional. RDF predicate: `foaf:name`.

`has_name(string: str)` / `get_name() -> str | None` / `remove_name()`

The full name of the agent. For organizations, this is their name. For people, typically "Given Family" (but prefer `has_given_name()` + `has_family_name()` for people when both parts are known).

### given name

Functional. RDF predicate: `foaf:givenName`.

`has_given_name(string: str)` / `get_given_name() -> str | None` / `remove_given_name()`

### family name

Functional. RDF predicate: `foaf:familyName`.

`has_family_name(string: str)` / `get_family_name() -> str | None` / `remove_family_name()`

### related agents

Non-functional. RDF predicate: `dcterms:relation`. Values are URI strings.

`has_related_agent(thing_res: str)` / `get_related_agents() -> list[str]` / `remove_related_agent(thing_res=None)`

External URIs of related agents, for inter-linking purposes.

## Example

```python
g_set = GraphSet("https://w3id.org/oc/meta/")
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

ra = g_set.add_ra(resp_agent)
ra.has_given_name("Arcangelo")
ra.has_family_name("Massari")

orcid = g_set.add_id(resp_agent)
orcid.create_orcid("0000-0002-8420-0696")
ra.has_identifier(orcid)
```
