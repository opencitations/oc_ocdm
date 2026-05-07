---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: BibliographicResource
description: Published resource that cites or is cited by other resources.
---

A published bibliographic resource: an article, book, dataset, thesis, or any other citable work. Created via `GraphSet.add_br(resp_agent)`. Short name: `br`. OCDM class: `fabio:Expression`.

## Properties

### title

Functional. RDF predicate: `dcterms:title`.

`has_title(string: str)` / `get_title() -> str | None` / `remove_title()`

### subtitle

Functional. RDF predicate: `fabio:hasSubtitle`.

`has_subtitle(string: str)` / `get_subtitle() -> str | None` / `remove_subtitle()`

### container

Functional. RDF predicate: `frbr:partOf`. Accepts: `BibliographicResource`.

`is_part_of(br_res)` / `get_is_part_of() -> BibliographicResource | None` / `remove_is_part_of()`

Models the containment hierarchy: an article is part of an issue, which is part of a volume, which is part of a journal.

### citations

Non-functional. RDF predicate: `cito:cites`. Accepts: `BibliographicResource`.

`has_citation(br_res)` / `get_citations() -> list[BibliographicResource]` / `remove_citation(br_res=None)`

Shorthand for a direct `cito:cites` triple between two resources. For richer citation data (characterization, provenance), use the [`Citation`](../citation/) entity instead.

### publication date

Functional. RDF predicate: `prism:publicationDate`.

`has_pub_date(string: str)` / `get_pub_date() -> str | None` / `remove_pub_date()`

The value must be ISO 8601. The library automatically determines the appropriate XSD datatype (`xsd:date`, `xsd:gYearMonth`, or `xsd:gYear`) from the string precision.

### formats

Non-functional. RDF predicate: `frbr:embodiment`. Accepts: `ResourceEmbodiment`.

`has_format(re_res)` / `get_formats() -> list[ResourceEmbodiment]` / `remove_format(re_res=None)`

### number

Functional. RDF predicate: `fabio:hasSequenceIdentifier`.

`has_number(string: str)` / `get_number() -> str | None` / `remove_number()`

A sequence identifier within a collection: an article number in an issue, a volume number in a journal, a chapter number in a book.

### edition

Functional. RDF predicate: `prism:edition`.

`has_edition(string: str)` / `get_edition() -> str | None` / `remove_edition()`

### bibliographic references

Non-functional. RDF predicate: `frbr:part`. Accepts: `BibliographicReference`.

`contains_in_reference_list(be_res)` / `get_contained_in_reference_lists() -> list[BibliographicReference]` / `remove_contained_in_reference_list(be_res=None)`

Entries in the resource's reference list.

### discourse elements

Non-functional. RDF predicate: `frbr:part`. Accepts: `DiscourseElement`.

`contains_discourse_element(de_res)` / `get_contained_discourse_elements() -> list[DiscourseElement]` / `remove_contained_discourse_element(de_res=None)`

Structural parts of the document (sections, paragraphs, etc.).

### contributors

Non-functional. RDF predicate: `pro:isDocumentContextFor`. Accepts: `AgentRole`.

`has_contributor(ar_res)` / `get_contributors() -> list[AgentRole]` / `remove_contributor(ar_res=None)`

### related documents

Non-functional. RDF predicate: `dcterms:relation`. Values are URI strings.

`has_related_document(thing_res: str)` / `get_related_documents() -> list[str]` / `remove_related_document(thing_res=None)`

External URIs for related resources (e.g. a preprint in another repository).

## Type classification

Each `create_*` method sets a secondary `rdf:type`. Calling any of them replaces the previous secondary type. Use `remove_type()` to strip it.

### Articles

| Method | RDF type |
|---|---|
| `create_journal_article()` | `fabio:JournalArticle` |
| `create_journal_editorial()` | `fabio:JournalEditorial` |
| `create_editorial()` | `fabio:Editorial` |
| `create_proceedings_article()` | `fabio:ProceedingsPaper` |
| `create_newspaper_article()` | `fabio:NewspaperArticle` |
| `create_newspaper_editorial()` | `fabio:NewspaperEditorial` |

### Books

| Method | RDF type |
|---|---|
| `create_book()` | `fabio:Book` |
| `create_edited_book()` | `fabio:Book` |
| `create_monograph()` | `fabio:Book` |
| `create_book_chapter()` | `fabio:BookChapter` |
| `create_book_part()` | `doco:Part` |
| `create_book_section()` | `fabio:ExpressionCollection` |
| `create_book_set()` | `fabio:BookSet` |
| `create_book_track()` | `fabio:Expression` |
| `create_reference_book()` | `fabio:ReferenceBook` |
| `create_reference_entry()` | `fabio:ReferenceEntry` |

### Serials

| Method | RDF type |
|---|---|
| `create_journal()` | `fabio:Journal` |
| `create_volume()` | `fabio:JournalVolume` |
| `create_issue()` | `fabio:JournalIssue` |
| `create_newspaper()` | `fabio:Newspaper` |
| `create_newspaper_issue()` | `fabio:NewspaperIssue` |
| `create_series()` | `fabio:Series` |
| `create_book_series()` | `fabio:BookSeries` |

### Proceedings and reports

| Method | RDF type |
|---|---|
| `create_proceedings()` | `fabio:AcademicProceedings` |
| `create_proceedings_series()` | `fabio:Series` |
| `create_report()` | `fabio:ReportDocument` |
| `create_report_series()` | `fabio:Series` |

### Other types

| Method | RDF type |
|---|---|
| `create_dataset()` | `fabio:DataFile` |
| `create_dissertation()` | `fabio:Thesis` |
| `create_preprint()` | `fabio:Preprint` |
| `create_peer_review()` | `fr:ReviewVersion` |
| `create_presentation()` | `fabio:Presentation` |
| `create_abstract()` | `doco:Abstract` |
| `create_archival_document()` | `fabio:ArchivalDocument` |
| `create_audio_document()` | `fabio:AudioDocument` |
| `create_computer_program()` | `fabio:ComputerProgram` |
| `create_data_management_plan()` | `fabio:DataManagementPlan` |
| `create_retraction_notice()` | `fabio:RetractionNotice` |
| `create_standard()` | `fabio:SpecificationDocument` |
| `create_standard_series()` | `fabio:Series` |
| `create_expression_collection()` | `fabio:ExpressionCollection` |
| `create_web_content()` | `fabio:WebContent` |
| `create_component()` | `fabio:Expression` |
| `create_other()` | `fabio:Expression` |

## Example

```python
from oc_ocdm.graph import GraphSet

g_set = GraphSet("https://w3id.org/oc/meta/")
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

journal = g_set.add_br(resp_agent)
journal.create_journal()
journal.has_title("Quantitative Science Studies")

volume = g_set.add_br(resp_agent)
volume.create_volume()
volume.has_number("5")
volume.is_part_of(journal)

issue = g_set.add_br(resp_agent)
issue.create_issue()
issue.has_number("1")
issue.is_part_of(volume)

article = g_set.add_br(resp_agent)
article.create_journal_article()
article.has_title("OpenCitations Meta")
article.has_pub_date("2024-03")
article.is_part_of(issue)

doi = g_set.add_id(resp_agent)
doi.create_doi("10.1162/qss_a_00292")
article.has_identifier(doi)

re = g_set.add_re(resp_agent)
re.create_digital_embodiment()
re.has_starting_page("50")
re.has_ending_page("75")
article.has_format(re)
```
