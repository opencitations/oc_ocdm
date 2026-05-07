---
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

title: GraphSet
description: Create, retrieve and manage graph entities through the GraphSet container.
---

`GraphSet` is the container for all graph entities. It handles entity creation, IRI generation, counter management and entity retrieval.

```python
from oc_ocdm.graph import GraphSet

g_set = GraphSet("https://w3id.org/oc/meta/")
```

## Constructor

```python
GraphSet(
    base_iri: str,
    info_dir: str = "",
    supplier_prefix: str = "",
    wanted_label: bool = True,
    custom_counter_handler: CounterHandler | None = None
)
```

| Parameter | Purpose |
|---|---|
| `base_iri` | Root IRI for all entities (e.g. `https://w3id.org/oc/meta/`) |
| `info_dir` | Directory for counter file persistence. When set, a `FilesystemCounterHandler` is used |
| `supplier_prefix` | Numeric prefix identifying the data source within IRIs (e.g. `"060"`) |
| `wanted_label` | Generate `rdfs:label` triples for new entities |
| `custom_counter_handler` | Override the default counter strategy. See [Counter handlers](../counter_handlers/) |

## Creating entities

Each OCDM entity type has a factory method. They all share the same signature:

```python
g_set.add_br(
    resp_agent: str | None,
    source: str | None = None,
    res: str | None = None,
    preexisting_graph: SubgraphView | None = None
)
```

| Parameter | Purpose |
|---|---|
| `resp_agent` | IRI of the agent responsible for the change |
| `source` | Provenance source IRI |
| `res` | Use a specific IRI instead of auto-generating one |
| `preexisting_graph` | Prior state for diff-based tracking (see [Provenance](../provenance/#change-tracking)) |

When `res` matches an entity already in the set, the existing entity is returned.

| Factory method | Return type | OCDM class |
|---|---|---|
| `add_br()` | [`BibliographicResource`](../../entities/bibliographic_resource/) | `fabio:Expression` |
| `add_ra()` | [`ResponsibleAgent`](../../entities/responsible_agent/) | `foaf:Agent` |
| `add_ar()` | [`AgentRole`](../../entities/agent_role/) | `pro:RoleInTime` |
| `add_id()` | [`Identifier`](../../entities/identifier/) | `datacite:Identifier` |
| `add_ci()` | [`Citation`](../../entities/citation/) | `cito:Citation` |
| `add_be()` | [`BibliographicReference`](../../entities/bibliographic_reference/) | `biro:BibliographicReference` |
| `add_re()` | [`ResourceEmbodiment`](../../entities/resource_embodiment/) | `fabio:Manifestation` |
| `add_de()` | [`DiscourseElement`](../../entities/discourse_element/) | `deo:DiscourseElement` |
| `add_an()` | [`ReferenceAnnotation`](../../entities/reference_annotation/) | `oa:Annotation` |
| `add_pl()` | [`PointerList`](../../entities/pointer_list/) | `c4o:SingleLocationPointerList` |
| `add_rp()` | [`ReferencePointer`](../../entities/reference_pointer/) | `c4o:InTextReferencePointer` |

## Retrieving entities

Look up a single entity by IRI:

```python
entity = g_set.get_entity("https://w3id.org/oc/meta/br/0605")
```

Returns `None` if the IRI is not in the set.

Typed getters return tuples of all entities of a given type:

```python
all_br: tuple[BibliographicResource, ...] = g_set.get_br()
all_ra: tuple[ResponsibleAgent, ...] = g_set.get_ra()
```

One getter exists per entity type: `get_an()`, `get_ar()`, `get_be()`, `get_br()`, `get_ci()`, `get_de()`, `get_id()`, `get_pl()`, `get_ra()`, `get_re()`, `get_rp()`.

## Orphan detection

`get_orphans()` returns entities that no other entity in the set references (i.e. they never appear as the object of a triple):

```python
orphans = g_set.get_orphans()
```

To remove orphan references from a SPARQL triplestore, call `remove_orphans_from_triplestore()`. It queries the triplestore for entities that reference deleted entities, imports them into the `GraphSet`, and removes those references locally. The triplestore itself is updated when you later call `store_all()` or `upload_all()`:

```python
g_set.remove_orphans_from_triplestore("http://localhost:9999/sparql", resp_agent)
```

## Committing changes

After generating provenance and storing data, call `commit_changes()` to reset change tracking. See [Provenance](../provenance/#change-tracking) for details.

```python
g_set.commit_changes()
```
