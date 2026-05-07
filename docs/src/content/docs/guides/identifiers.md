---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: Identifiers
description: Assign DOIs, ORCIDs, ISBNs and other identifier schemes to entities.
---

Every bibliographic entity in the OCDM can carry external identifiers through the `Identifier` class. An identifier consists of a scheme (DOI, ORCID, etc.) and a literal value.

## Creating an identifier

Create an `Identifier` via `GraphSet.add_id()`, set its scheme and value with one of the scheme-specific methods, then attach it to an entity:

```python
from oc_ocdm.graph import GraphSet

base_iri = "https://w3id.org/oc/meta/"
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

g_set = GraphSet(base_iri)
br = g_set.add_br(resp_agent)
br.has_title("OpenCitations Meta")

doi = g_set.add_id(resp_agent)
doi.create_doi("10.1162/qss_a_00292")
br.has_identifier(doi)
```

Each `create_*` method sets both the scheme and the literal value in a single call. Calling a second `create_*` on the same identifier replaces the previous scheme and value.

## Supported schemes

| Method | Scheme |
|---|---|
| `create_doi(value)` | DOI |
| `create_orcid(value)` | ORCID |
| `create_isbn(value)` | ISBN |
| `create_issn(value)` | ISSN |
| `create_pmid(value)` | PubMed ID |
| `create_pmcid(value)` | PubMed Central ID |
| `create_arxiv(value)` | arXiv ID |
| `create_url(value)` | URL |
| `create_wikidata(value)` | Wikidata QID |
| `create_wikipedia(value)` | Wikipedia page |
| `create_crossref(value)` | Crossref ID |
| `create_datacite(value)` | DataCite ID |
| `create_viaf(value)` | VIAF ID |
| `create_openalex(value)` | OpenAlex ID |
| `create_oci(value)` | OpenCitations Identifier |
| `create_intrepid(value)` | [InTRePID](https://doi.org/10.6084/m9.figshare.11674032) (In-Text Reference Pointer Identifier) |
| `create_jid(value)` | [JID](https://japanlinkcenter.org/top/english.html) (Japan Link Center journal identifier) |
| `create_xpath(value)` | XPath expression (local identifier for locating elements in XML sources) |
| `create_xmlid(value)` | XML ID (local identifier referencing an element's `id` attribute in XML sources) |

## Reading identifier data

```python
scheme = doi.get_scheme()
value = doi.get_literal_value()
```

`get_scheme()` returns the scheme IRI as a string. `get_literal_value()` returns the literal value.

## Multiple identifiers on one entity

An entity can have multiple identifiers. All `BibliographicEntity` subclasses (which includes all 11 graph entity types) inherit `has_identifier()`, `get_identifiers()`, `remove_identifier()`, and `remove_duplicated_identifiers()`:

```python
doi = g_set.add_id(resp_agent)
doi.create_doi("10.1162/qss_a_00292")

issn = g_set.add_id(resp_agent)
issn.create_issn("2641-3337")

br.has_identifier(doi)
br.has_identifier(issn)

all_ids = br.get_identifiers()
```

To remove duplicates (identifiers with the same scheme and value):

```python
br.remove_duplicated_identifiers()
```

## Identifiers on agents

The same pattern applies to responsible agents. For example, attaching an ORCID:

```python
ra = g_set.add_ra(resp_agent)
ra.has_given_name("Arcangelo")
ra.has_family_name("Massari")

orcid = g_set.add_id(resp_agent)
orcid.create_orcid("0000-0002-8420-0696")
ra.has_identifier(orcid)
```
