---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: Reading data
description: Import entities from RDF files and SPARQL endpoints.
---

The `Reader` class loads RDF data from files or SPARQL endpoints into a `GraphSet`. Imported entities carry their preexisting state, so any modifications you apply afterward are tracked as diffs.

## From files

`Reader.load()` reads an RDF file and returns an `rdflib.Dataset`. It detects the format from the file extension:

| Extension | Format |
|---|---|
| `.json`, `.jsonld` | JSON-LD |
| `.xml`, `.rdf` | RDF/XML |
| `.ttl` | Turtle |
| `.nt` | N-Triples |
| `.nq` | N-Quads |
| `.trig` | TriG |

ZIP archives containing any of these formats are also supported.

```python
from oc_ocdm import Reader
from oc_ocdm.graph import GraphSet

reader = Reader()
dataset = reader.load("data.jsonld")
```

To turn the loaded data into entity objects, pass it to `import_entities_from_graph()` along with a `GraphSet`:

```python
base_iri = "https://w3id.org/oc/meta/"
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

g_set = GraphSet(base_iri)
entities = Reader.import_entities_from_graph(g_set, dataset, resp_agent)
```

The method inspects the `rdf:type` of each subject in the graph and instantiates the matching entity class. The returned list contains all imported entities; they are also added to the `GraphSet`.

The second argument (`dataset` in the example above) accepts several types besides `rdflib.Dataset`: a [`TripleLite`](https://opencitations.github.io/triplelite/) graph, an `rdflib.Graph`, or the `results.bindings` array from a SPARQL JSON response ([W3C SPARQL Query Results JSON Format](https://www.w3.org/TR/sparql11-results-json/)) with variables `s`, `p`, `o`.

## From a SPARQL endpoint

To load entities directly from a triplestore, use `import_entities_from_triplestore()`. Pass a list of entity IRIs and the SPARQL endpoint URL:

```python
entities = Reader.import_entities_from_triplestore(
    g_set,
    "https://opencitations.net/meta/sparql",
    ["https://w3id.org/oc/meta/br/0605", "https://w3id.org/oc/meta/br/0636066666"],
    resp_agent
)
```

For large numbers of entities, the method queries them in batches. The default batch size is 1000; adjust it with the `batch_size` parameter:

```python
entities = Reader.import_entities_from_triplestore(
    g_set,
    "https://opencitations.net/meta/sparql",
    large_entity_list,
    resp_agent,
    batch_size=500
)
```

## Validation

`Reader.graph_validation()` runs SHACL validation against the OCDM schema. It takes an `rdflib.Graph` and returns the validated graph:

```python
reader = Reader()
dataset = reader.load("data.jsonld")
validated = reader.graph_validation(dataset)
```

By default, validation uses an open schema that allows additional properties beyond the OCDM specification. Pass `closed=True` for strict validation:

```python
validated = reader.graph_validation(dataset, closed=True)
```

You can also enable validation during import:

```python
entities = Reader.import_entities_from_graph(
    g_set, dataset, resp_agent, enable_validation=True, closed=True
)
```

## Context maps

JSON-LD files reference an `@context` by URL. When rdflib parses such a file, it needs the context content to resolve compact property names into full IRIs. By default it would fetch the URL over the network on every call. A `context_map` provides a local copy to avoid that:

```python
reader = Reader(context_map={
    "https://w3id.org/oc/meta/context.json": "/data/oc_context.json"
})
```

The reader loads each local file once at initialization and reuses it for all subsequent operations. The same `context_map` parameter is available on the `Storer` constructor for serialization (see [Storing data](../storing/)).
