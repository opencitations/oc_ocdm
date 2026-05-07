---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: Citation
description: Directional link from a citing resource to a cited resource.
---

A citation is a directional link from one bibliographic resource to another. It captures when the citation was made, how much time elapsed between the publications, and optionally the type of citation (self-citation, distant citation, etc.). Created via `GraphSet.add_ci(resp_agent)`. Short name: `ci`. OCDM class: `cito:Citation`.

## Properties

### citing entity

Functional. RDF predicate: `cito:hasCitingEntity`. Accepts: `BibliographicResource`.

`has_citing_entity(citing_res)` / `get_citing_entity() -> BibliographicResource | None` / `remove_citing_entity()`

### cited entity

Functional. RDF predicate: `cito:hasCitedEntity`. Accepts: `BibliographicResource`.

`has_cited_entity(cited_res)` / `get_cited_entity() -> BibliographicResource | None` / `remove_cited_entity()`

### citation creation date

Functional. RDF predicate: `cito:hasCitationCreationDate`.

`has_citation_creation_date(string: str)` / `get_citation_creation_date() -> str | None` / `remove_citation_creation_date()`

ISO 8601 string. Typically matches the publication date of the citing resource.

### citation time span

Functional. RDF predicate: `cito:hasCitationTimeSpan`.

`has_citation_time_span(string: str)` / `get_citation_time_span() -> str | None` / `remove_citation_time_span()`

`xsd:duration` string (e.g. `"P4Y"` for four years). The interval between the publication dates of cited and citing resources.

### citation characterization

Functional. RDF predicate: `cito:hasCitationCharacterisation`. Values are URI strings.

`has_citation_characterization(thing_res: str)` / `get_citation_characterization() -> str | None` / `remove_citation_characterization()`

## Type classification

| Method | RDF type |
|---|---|
| `create_self_citation()` | `cito:SelfCitation` |
| `create_author_self_citation()` | `cito:AuthorSelfCitation` |
| `create_author_network_self_citation()` | `cito:AuthorNetworkSelfCitation` |
| `create_affiliation_self_citation()` | `cito:AffiliationSelfCitation` |
| `create_funder_self_citation()` | `cito:FunderSelfCitation` |
| `create_journal_self_citation()` | `cito:JournalSelfCitation` |
| `create_journal_cartel_citation()` | `cito:JournalCartelCitation` |
| `create_distant_citation()` | `cito:DistantCitation` |

## Example

```python
g_set = GraphSet("https://w3id.org/oc/meta/")
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

citing = g_set.add_br(resp_agent)
citing.has_title("OpenCitations Meta")
citing.has_pub_date("2024-03")

cited = g_set.add_br(resp_agent)
cited.has_title("Automatic generation of citation data")
cited.has_pub_date("2020-03")

ci = g_set.add_ci(resp_agent)
ci.has_citing_entity(citing)
ci.has_cited_entity(cited)
ci.has_citation_creation_date("2024-03")
ci.has_citation_time_span("P4Y")
ci.create_distant_citation()
```
