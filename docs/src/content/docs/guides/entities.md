---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: Entities
description: The 11 graph entity types, property patterns, and entity lifecycle operations.
---

The OCDM organizes data into three layers:

- **Graph entities** represent bibliographic data: articles, authors, citations, identifiers and so on.
- **Provenance entities** record how graph entities change over time (see [Provenance](/guides/provenance/)).
- **Metadata entities** describe datasets and their distributions at a higher level.

This guide covers graph entities. Each layer has a corresponding set class that holds entities and provides methods to create them: `GraphSet`, `ProvSet`, `MetadataSet`.

## Entity types

`GraphSet` provides a factory method for each of the 11 entity types defined by the OCDM. Every factory method requires a `resp_agent` string (the IRI of the agent responsible for the change) and returns the new entity:

| Method | Return type | OCDM class |
|---|---|---|
| `add_br()` | `BibliographicResource` | fabio:Expression |
| `add_ra()` | `ResponsibleAgent` | foaf:Agent |
| `add_ar()` | `AgentRole` | pro:RoleInTime |
| `add_id()` | `Identifier` | datacite:Identifier |
| `add_ci()` | `Citation` | cito:Citation |
| `add_be()` | `BibliographicReference` | biro:BibliographicReference |
| `add_re()` | `ResourceEmbodiment` | fabio:Manifestation |
| `add_de()` | `DiscourseElement` | deo:DiscourseElement |
| `add_an()` | `ReferenceAnnotation` | oa:Annotation |
| `add_pl()` | `PointerList` | c4o:SingleLocationPointerList |
| `add_rp()` | `ReferencePointer` | c4o:InTextReferencePointer |

```python
from oc_ocdm.graph import GraphSet

base_iri = "https://w3id.org/oc/meta/"
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

g_set = GraphSet(base_iri)
br = g_set.add_br(resp_agent)
ra = g_set.add_ra(resp_agent)
```

Each entity receives an auto-generated IRI based on the base IRI and an internal counter. To instantiate an entity with a known IRI, pass it as the `res` parameter:

```python
br = g_set.add_br(resp_agent, res="https://w3id.org/oc/meta/br/0605")
```

If the IRI already exists in the set, the existing entity is returned instead of creating a duplicate.

## Property patterns

Entity properties follow a consistent naming convention:

- `has_X(value)` sets or adds a value
- `get_X()` returns the current value (or `None`)
- `remove_X(value)` removes a value

Some properties are single-valued: calling `has_title()` twice overwrites the first title. Others are multi-valued: calling `has_related_document()` twice adds two documents.

For multi-valued properties, `remove_X()` without arguments removes all values. With an argument, it removes only that specific value:

```python
br.has_related_document("https://w3id.org/oc/meta/br/1")
br.has_related_document("https://w3id.org/oc/meta/br/2")
br.remove_related_document("https://w3id.org/oc/meta/br/1")
```

## Preexisting graph

An entity can be created in two modes depending on whether its prior state is known.

When no prior state is provided, the entity operates in **append mode**: all triples produced by setter calls are added to whatever already exists in the store. RDF semantics prevent duplicates, so adding an existing triple is a no-op.

When a `preexisting_graph` (a [`SubgraphView`](https://opencitations.github.io/triplelite/guide/subgraph/#subgraphview-is-a-live-view)) is passed to a factory method, the entity's graph is populated with the preexisting triples. The library then compares the new state against the old one and computes the exact set of triples to add and remove.

You can pass `preexisting_graph` directly:

```python
from triplelite import TripleLite, RDFTerm

existing = TripleLite()
existing.add(("https://w3id.org/oc/meta/br/0605", "http://purl.org/dc/terms/title", RDFTerm("literal", "Old title")))

br = g_set.add_br(
    resp_agent,
    res="https://w3id.org/oc/meta/br/0605",
    preexisting_graph=existing.subgraph("https://w3id.org/oc/meta/br/0605")
)
br.has_title("New title")
```

In this example, the library knows the entity previously had "Old title" and now has "New title", so it can produce a diff (remove old, add new) rather than blindly appending.

`Reader.import_entities_from_graph()` does this automatically: for each subject in the loaded graph, it extracts the [`SubgraphView`](https://opencitations.github.io/triplelite/guide/subgraph/#subgraphview-is-a-live-view) and passes it as `preexisting_graph` to the corresponding factory method. See [Reading data](/guides/reading/) for details.

## Merging entities

Two entities of the same type can be merged. The surviving entity absorbs the triples of the other, which is marked for deletion:

```python
br_1 = g_set.add_br(resp_agent)
br_2 = g_set.add_br(resp_agent)
br_1.has_title("OpenCitations Meta")
br_2.has_title("OpenCitations Meta: open bibliographic metadata")

br_1.merge(br_2)
```

By default, when both entities have a value for the same single-valued property, the merged entity keeps the value from `other`. Pass `prefer_self=True` to keep the surviving entity's value instead.

## Deletion and restoration

Marking an entity for deletion removes all its triples:

```python
br.mark_as_to_be_deleted()
```

A deleted entity can be restored before changes are committed:

```python
br.mark_as_restored()
```

## Committing changes

After generating provenance and storing data, call `commit_changes()` on the set to reset the internal change-tracking state. This prepares the set for a new round of modifications:

```python
g_set.commit_changes()
```

Without this call, the library cannot distinguish new changes from previously recorded ones.

## Retrieving entities

`GraphSet` provides typed getters that return tuples of entities currently in the set:

```python
all_br = g_set.get_br()
all_ra = g_set.get_ra()
```

To look up a single entity by IRI:

```python
entity = g_set.get_entity("https://w3id.org/oc/meta/br/0605")
```

## BibliographicResource

`BibliographicResource` is the largest entity class, with methods for titles, dates, contributors, related documents, formats, and document type classification.

Properties include `has_title()`, `has_subtitle()`, `has_pub_date()`, `has_number()`, `has_edition()`, and relationships like `is_part_of()`, `has_citation()`, `has_contributor()`, `has_format()`, `contains_in_reference_list()`, `contains_discourse_element()`, `has_related_document()`.

Type creation methods set the specific document type: `create_journal_article()`, `create_book()`, `create_book_chapter()`, `create_proceedings_article()`, `create_dataset()`, `create_dissertation()`, `create_preprint()`, `create_journal()`, `create_volume()`, `create_issue()`, and many others.

```python
article = g_set.add_br(resp_agent)
article.has_title("OpenCitations Meta")
article.has_pub_date("2024-03")
article.create_journal_article()

volume = g_set.add_br(resp_agent)
volume.create_volume()
volume.has_number("5")
article.is_part_of(volume)
```

## ResponsibleAgent

Represents a person or organization.

```python
ra = g_set.add_ra(resp_agent)
ra.has_given_name("Arcangelo")
ra.has_family_name("Massari")
```

For organizations, use `has_name()` instead.

## AgentRole

Links a `ResponsibleAgent` to a `BibliographicResource` through a role:

```python
ar = g_set.add_ar(resp_agent)
ar.is_held_by(ra)
ar.create_author()
article.has_contributor(ar)
```

Available roles: `create_author()`, `create_editor()`, `create_publisher()`.

Roles can be ordered with `has_next()`:

```python
ra_2 = g_set.add_ra(resp_agent)
ra_2.has_given_name("Fabio")
ra_2.has_family_name("Mariani")

ar_second = g_set.add_ar(resp_agent)
ar_second.is_held_by(ra_2)
ar_second.create_author()
ar.has_next(ar_second)
article.has_contributor(ar_second)
```

## Citation

Represents a citation relationship between two bibliographic resources:

```python
citing_br = g_set.add_br(resp_agent)
citing_br.has_title("OpenCitations Meta")

cited_br = g_set.add_br(resp_agent)
cited_br.has_title("Automatic generation of citation data")

ci = g_set.add_ci(resp_agent)
ci.has_citing_entity(citing_br)
ci.has_cited_entity(cited_br)
ci.has_citation_creation_date("2024-03")
ci.has_citation_time_span("P4Y")
```

Citation characterization methods: `create_self_citation()`, `create_author_self_citation()`, `create_journal_self_citation()`, `create_distant_citation()`, and others.

## Other entity types

**BibliographicReference** stores the textual content of a reference list entry and links it to the cited resource:

```python
be = g_set.add_be(resp_agent)
be.has_content("Heibi, I., Peroni, S., & Shotton, D. (2019). Software review: COCI, the OpenCitations Index of Crossref open DOI-to-DOI citations. Scientometrics, 121, 1213-1228.")
be.references_br(cited_br)
```

**ResourceEmbodiment** represents a specific manifestation (digital or print) of a bibliographic resource:

```python
re = g_set.add_re(resp_agent)
re.create_digital_embodiment()
re.has_media_type("http://purl.org/NET/mediatypes/application/pdf")
re.has_url("https://direct.mit.edu/qss/article-pdf/5/1/50/2373930/qss_a_00292.pdf")
re.has_starting_page("50")
re.has_ending_page("75")
article.has_format(re)
```

**DiscourseElement** represents a structural part of a document (section, paragraph, sentence). It supports nesting, ordering and type classification:

```python
de = g_set.add_de(resp_agent)
de.create_section()
de.has_title("Introduction")
```

**ReferenceAnnotation** links an in-text citation to its citation entity:

```python
an = g_set.add_an(resp_agent)
an.has_body_annotation(ci)
```

**PointerList** and **ReferencePointer** model in-text reference pointers and their groupings.
