---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: Metadata
description: Describe datasets and distributions with MetadataSet, Dataset and Distribution.
---

The metadata layer sits above the graph layer: while graph entities represent individual bibliographic records, metadata entities describe the datasets that contain them.

## MetadataSet

`MetadataSet` mirrors `GraphSet` for the metadata layer.

```python
from oc_ocdm.metadata import MetadataSet

m_set = MetadataSet("https://w3id.org/oc/meta/")
```

### Constructor

```python
MetadataSet(
    base_iri: str,
    info_dir: str = "",
    wanted_label: bool = True
)
```

`info_dir` controls counter persistence, same as `GraphSet`. No `supplier_prefix` or `custom_counter_handler` here: `MetadataSet` uses `FilesystemCounterHandler` when `info_dir` is set, `InMemoryCounterHandler` otherwise.

### Factory methods

```python
dataset = m_set.add_dataset(dataset_name, resp_agent, source=None, res=None, preexisting_graph=None)
di = m_set.add_di(dataset_name, resp_agent, source=None, res=None, preexisting_graph=None)
```

Both require a `dataset_name` string that groups related metadata entities. `add_dataset()` returns a `Dataset`, `add_di()` returns a `Distribution`.

### Retrieval

```python
m_set.get_entity(res)           # by IRI, returns MetadataEntity | None
m_set.get_dataset()             # tuple[Dataset, ...]
m_set.get_di()                  # tuple[Distribution, ...]
```

### Committing

```python
m_set.commit_changes()
```

Resets change tracking and removes entities marked for deletion, same as `GraphSet.commit_changes()`.

## Dataset

A DCAT Dataset: a named collection of data. All properties are functional (single-valued) unless noted otherwise.

### title

`has_title(string: str)` / `get_title() -> str | None` / `remove_title()`

RDF predicate: `dcterms:title`.

### description

`has_description(string: str)` / `get_description() -> str | None` / `remove_description()`

RDF predicate: `dcterms:description`.

### publication date

`has_publication_date(string: str)` / `get_publication_date() -> str | None` / `remove_publication_date()`

The value must be an `xsd:dateTime` string. RDF predicate: `dcterms:issued`.

### modification date

`has_modification_date(string: str)` / `get_modification_date() -> str | None` / `remove_modification_date()`

Same format as publication date. RDF predicate: `dcterms:modified`.

### keywords (non-functional)

`has_keyword(string: str)` / `get_keywords() -> list[str]` / `remove_keyword(string: str | None = None)`

RDF predicate: `dcat:keyword`.

### subjects (non-functional)

`has_subject(thing_res: str)` / `get_subjects() -> list[str]` / `remove_subject(thing_res: str | None = None)`

Values are URIs. RDF predicate: `dcat:theme`.

### landing page

`has_landing_page(thing_res: str)` / `get_landing_page() -> str | None` / `remove_landing_page()`

A browsable HTML page for the dataset. RDF predicate: `dcat:landingPage`.

### sub-datasets (non-functional)

`has_sub_dataset(obj: Dataset)` / `get_sub_datasets() -> list[Dataset]` / `remove_sub_dataset(dataset_res: Dataset | None = None)`

RDF predicate: `void:subset`.

### SPARQL endpoint

`has_sparql_endpoint(thing_res: str)` / `get_sparql_endpoint() -> str | None` / `remove_sparql_endpoint()`

RDF predicate: `void:sparqlEndpoint`.

### distributions (non-functional)

`has_distribution(obj: Distribution)` / `get_distributions() -> list[Distribution]` / `remove_distribution(di_res: Distribution | None = None)`

RDF predicate: `dcat:distribution`.

## Distribution

A DCAT Distribution: an accessible form of a dataset (e.g. a downloadable file). All properties are functional.

### title

`has_title(string: str)` / `get_title() -> str | None` / `remove_title()`

RDF predicate: `dcterms:title`.

### description

`has_description(string: str)` / `get_description() -> str | None` / `remove_description()`

RDF predicate: `dcterms:description`.

### publication date

`has_publication_date(string: str)` / `get_publication_date() -> str | None` / `remove_publication_date()`

`xsd:dateTime` string. RDF predicate: `dcterms:issued`.

### byte size

`has_byte_size(string: str)` / `get_byte_size() -> str | None` / `remove_byte_size()`

`xsd:decimal` string. RDF predicate: `dcat:byteSize`.

### license

`has_license(thing_res: str)` / `get_license() -> str | None` / `remove_license()`

URI of the license resource. RDF predicate: `dcterms:license`.

### download URL

`has_download_url(thing_res: str)` / `get_download_url() -> str | None` / `remove_download_url()`

RDF predicate: `dcat:downloadURL`.

### media type

`has_media_type(thing_res: str)` / `get_media_type() -> str | None` / `remove_media_type()`

IANA media type URI. RDF predicate: `dcat:mediaType`.

## Example

```python
from oc_ocdm.metadata import MetadataSet
from oc_ocdm import Storer

m_set = MetadataSet("https://w3id.org/oc/meta/")
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

dataset = m_set.add_dataset("meta", resp_agent)
dataset.has_title("OpenCitations Meta")
dataset.has_description("Bibliographic metadata for all publications in OpenCitations indexes")
dataset.has_publication_date("2022-01-01T00:00:00")
dataset.has_sparql_endpoint("https://sparql.opencitations.net/meta")
dataset.has_landing_page("https://download.opencitations.net/")

di = m_set.add_di("meta", resp_agent)
di.has_title("OpenCitations Meta CSV dump")
di.has_media_type("https://www.iana.org/assignments/media-types/text/csv")
di.has_download_url("https://doi.org/10.5281/zenodo.15625650")
di.has_license("https://creativecommons.org/publicdomain/zero/1.0/")
dataset.has_distribution(di)

storer = Storer(m_set)
storer.store_graphs_in_file("meta_metadata.jsonld")
```
