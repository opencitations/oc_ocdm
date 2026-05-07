---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: Identifier
description: External identifier (DOI, ORCID, ISBN, etc.) for bibliographic entities.
---

An external identifier that can be attached to any entity inheriting from `BibliographicEntity`. An identifier pairs a scheme (DOI, ORCID, etc.) with a literal value. Created via `GraphSet.add_id(resp_agent)`. Short name: `id`. OCDM class: `datacite:Identifier`.

## Properties

### literal value and scheme

`get_literal_value() -> str | None` returns the identifier value (`literal:hasLiteralValue`).

`get_scheme() -> str | None` returns the scheme IRI (`datacite:usesIdentifierScheme`).

`remove_identifier_with_scheme()` removes both the literal value and the scheme in one call.

Both properties are always set together via one of the `create_*` methods below. Calling a second `create_*` on the same identifier replaces the previous scheme and value.

## Supported schemes

| Method | Scheme | Notes |
|---|---|---|
| `create_doi(value)` | DOI | Lowercased automatically |
| `create_orcid(value)` | ORCID | |
| `create_isbn(value)` | ISBN | |
| `create_issn(value)` | ISSN | Rejects `"0000-0000"` |
| `create_pmid(value)` | PubMed ID | |
| `create_pmcid(value)` | PubMed Central ID | |
| `create_arxiv(value)` | arXiv ID | |
| `create_url(value)` | URL | Lowercased and URL-encoded |
| `create_wikidata(value)` | Wikidata QID | |
| `create_wikipedia(value)` | Wikipedia page | |
| `create_crossref(value)` | Crossref ID | |
| `create_datacite(value)` | DataCite ID | |
| `create_viaf(value)` | VIAF ID | |
| `create_openalex(value)` | OpenAlex ID | |
| `create_oci(value)` | OpenCitations Identifier | |
| `create_intrepid(value)` | [InTRePID](https://doi.org/10.6084/m9.figshare.11674032) | |
| `create_jid(value)` | [JID](https://japanlinkcenter.org/top/english.html) | |
| `create_xpath(value)` | XPath expression | |
| `create_xmlid(value)` | XML ID | |

## Attaching identifiers to entities

All `BibliographicEntity` subclasses inherit these methods for managing identifiers:

| Method | Behaviour |
|---|---|
| `has_identifier(id_res: Identifier)` | Attaches an `Identifier` entity (non-functional) |
| `get_identifiers() -> list[Identifier]` | Returns all attached identifiers |
| `remove_identifier(id_res=None)` | Removes one or all identifiers |
| `remove_duplicated_identifiers()` | Deduplicates by scheme + literal value, merging duplicates |

## Example

```python
g_set = GraphSet("https://w3id.org/oc/meta/")
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

br = g_set.add_br(resp_agent)
br.has_title("OpenCitations Meta")

doi = g_set.add_id(resp_agent)
doi.create_doi("10.1162/qss_a_00292")
br.has_identifier(doi)

issn = g_set.add_id(resp_agent)
issn.create_issn("2641-3337")
br.has_identifier(issn)

all_ids = br.get_identifiers()
br.remove_duplicated_identifiers()
```
