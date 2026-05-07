---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: Storing data
description: Persist entities to RDF files or upload to SPARQL endpoints.
---

The `Storer` class writes the contents of a `GraphSet`, `ProvSet` or `MetadataSet` to files or uploads them to a SPARQL endpoint.

## Basic usage

```python
from oc_ocdm.graph import GraphSet
from oc_ocdm import Storer

base_iri = "https://w3id.org/oc/meta/"
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

g_set = GraphSet(base_iri)
br = g_set.add_br(resp_agent)
br.has_title("OpenCitations Meta")

storer = Storer(g_set)
storer.store_graphs_in_file("output.jsonld")
```

## Constructor parameters

`Storer` takes several optional parameters that control how output is organized:

```python
storer = Storer(
    g_set,
    output_format="json-ld",
    dir_split=10000,
    n_file_item=1000,
    default_dir="_",
    zip_output=False,
    context_map=None,
    modified_entities=None
)
```

**output_format**: the serialization format. Accepted values: `json-ld` (default), `nt`, `nt11`, `ntriples`, `application/n-triples`, `nquads`, `application/n-quads`.

**dir_split**: when using `store_all()`, this controls how entity files are distributed across subdirectories. A value of 10000 means entities 1 through 10000 go in one directory, 10001 through 20000 in the next, and so on. Set to 0 to put everything in a single directory.

**n_file_item**: the number of entities per output file when using `store_all()`.

**default_dir**: when `store_all()` organizes files, it groups them into subdirectories named after the entity's supplier prefix (the `060` in `https://w3id.org/oc/meta/br/0601`). Entities whose IRI has no supplier prefix (e.g. `https://w3id.org/oc/meta/br/1`) use `default_dir` as the subdirectory name instead. Defaults to `"_"`. See [Supplier prefixes](/guides/counter_handlers/#supplier-prefixes) for how prefixes work.

**zip_output**: if `True`, output files are compressed as ZIP archives.

**context_map**: maps JSON-LD `@context` URLs to local file paths. During serialization, rdflib uses the local copy to produce compact JSON-LD without fetching the URL over the network. The output file still references the original URL. See [Context maps](/guides/reading/#context-maps) for details.

**modified_entities**: an optional set of entity IRIs. When provided, only entities in this set are stored; others are skipped.

## Storing to files

Two methods are available.

`store_graphs_in_file()` writes all entities in the set to a single file:

```python
storer.store_graphs_in_file("output.jsonld")
```

Pass a `context_path` to embed a JSON-LD context:

```python
storer.store_graphs_in_file("output.jsonld", context_path="https://example.com/context.json")
```

`store_all()` distributes entities across a directory hierarchy following the OCDM file organization convention. It returns the list of file paths that were written:

```python
written_files = storer.store_all(
    base_dir="/data/rdf",
    base_iri=base_iri
)
```

The optional `process_id` parameter appends a suffix to file paths, useful for parallel processing to avoid file conflicts.

## Uploading to a SPARQL endpoint

`upload_all()` computes the SPARQL UPDATE queries for all entities in the set (based on the diff between their current and preexisting state) and sends them to the endpoint:

```python
storer.upload_all("https://opencitations.net/meta/sparql")
```

Queries are sent in batches. The default batch size is 10; adjust it with the `batch_size` parameter:

```python
storer.upload_all("https://opencitations.net/meta/sparql", batch_size=50)
```

To save the generated SPARQL queries to disk instead of executing them, pass `save_queries=True` and a `base_dir`:

```python
storer.upload_all(
    "https://opencitations.net/meta/sparql",
    base_dir="/data/queries",
    save_queries=True
)
```

`upload()` uploads a single entity:

```python
storer.upload(br, "https://opencitations.net/meta/sparql")
```

`execute_query()` runs an arbitrary SPARQL UPDATE query:

```python
storer.execute_query(
    "DELETE DATA { <https://w3id.org/oc/meta/br/0605> <http://purl.org/dc/terms/title> 'Old title' }",
    "https://opencitations.net/meta/sparql"
)
```

## Storing provenance and metadata

Provenance and metadata sets work the same way. Create a `Storer` for each set:

```python
from oc_ocdm.prov import ProvSet
from oc_ocdm.metadata import MetadataSet

prov_set = ProvSet(g_set, base_iri)
prov_set.generate_provenance()

prov_storer = Storer(prov_set)
prov_storer.store_graphs_in_file("provenance.jsonld")

meta_set = MetadataSet(base_iri)
dataset = meta_set.add_dataset("OpenCitations Meta", resp_agent)
dataset.has_modification_date("2024-03-01T00:00:00")

meta_storer = Storer(meta_set)
meta_storer.store_graphs_in_file("metadata.jsonld")
```
