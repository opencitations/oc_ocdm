---
title: Provenance
description: Track entity history with provenance snapshots, including merge and deletion scenarios.
---

The provenance layer records how graph entities change over time. Each time you call `generate_provenance()`, the library compares the current state of every entity in a `GraphSet` against its last known state and produces snapshot entities that describe what happened: creation, modification, merge or deletion.

## Basic workflow

Create a `ProvSet` from an existing `GraphSet`, make changes, then generate provenance:

```python
from oc_ocdm.graph import GraphSet
from oc_ocdm.prov import ProvSet
from oc_ocdm import Storer

base_iri = "https://w3id.org/oc/meta/"
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

g_set = GraphSet(base_iri)
prov_set = ProvSet(g_set, base_iri)

br = g_set.add_br(resp_agent)
br.has_title("OpenCitations Meta")

prov_set.generate_provenance()
g_set.commit_changes()
```

`generate_provenance()` inspects every entity in the `GraphSet` and creates `SnapshotEntity` instances inside the `ProvSet`. Each snapshot records the generation time, the responsible agent, the primary source (if any), and a description of what changed.

`commit_changes()` resets the internal change-tracking state of the `GraphSet` so the library can correctly detect changes in the next round.

## Snapshot types

The library distinguishes four types of snapshots, generated automatically based on what happened to each entity:

**Creation**: the entity is new and has no prior snapshot. The snapshot description reads "The entity has been created."

**Modification**: the entity existed before and its triples changed. The snapshot includes the SPARQL UPDATE query that transforms the old state into the new one. It derives from the previous snapshot.

**Merge**: the entity absorbed one or more other entities via `merge()`. The snapshot derives from both the entity's own previous snapshot and the last snapshots of the merged entities.

**Deletion**: the entity was marked for deletion with `mark_as_to_be_deleted()`. The snapshot records the invalidation of the entity.

## Growing provenance trees

This section walks through a multi-step lifecycle to show how the provenance tree grows. The example uses an in-memory counter handler (the default when no `info_dir` is specified), which is fine for demonstration but should not be used in production.

### Setup

```python
from oc_ocdm.graph import GraphSet
from oc_ocdm.prov import ProvSet
from oc_ocdm import Storer

base_iri = "https://w3id.org/oc/meta/"
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"

g_set = GraphSet(base_iri, wanted_label=False)
prov_set = ProvSet(g_set, base_iri, wanted_label=False)

graph_storer = Storer(g_set, output_format="json-ld")
prov_storer = Storer(prov_set, output_format="json-ld")
```

### Step 1: create three entities

```python
br_1 = g_set.add_br(resp_agent)
br_2 = g_set.add_br(resp_agent)
br_3 = g_set.add_br(resp_agent)

prov_set.generate_provenance()
g_set.commit_changes()

graph_storer.store_graphs_in_file("step1_graph.jsonld")
prov_storer.store_graphs_in_file("step1_prov.jsonld")
```

After this step, the provenance tree contains three creation snapshots, one per entity:

<img src="/images/step1.svg" alt="Provenance tree after step 1: three entities, each with a creation snapshot" style="background: white; padding: 1rem; border-radius: 8px;" />

### Step 2: create, modify and merge

The second round performs three operations:

1. Create a fourth entity.
2. Modify br/3 by adding a title and related documents.
3. Merge br/1 with br/2 (br/2 is implicitly deleted).

```python
br_4 = g_set.add_br(resp_agent)

br_3.has_title("OpenCitations Meta")
br_3.has_related_document("https://w3id.org/oc/meta/br/100")
br_3.has_related_document("https://w3id.org/oc/meta/br/200")
br_3.remove_related_document("https://w3id.org/oc/meta/br/100")

br_1.merge(br_2)

prov_set.generate_provenance()
g_set.commit_changes()

graph_storer.store_graphs_in_file("step2_graph.jsonld")
prov_storer.store_graphs_in_file("step2_prov.jsonld")
```

The provenance tree now has a second row of snapshots. Greyed-out nodes are from the previous step.

<img src="/images/step2.svg" alt="Provenance tree after step 2: br/1 merged with br/2, br/3 modified, br/4 created" style="background: white; padding: 1rem; border-radius: 8px;" />

The merge snapshot of br/1 derives from both br/1's previous snapshot and br/2's last snapshot. The deletion snapshot of br/2 records that it was merged into br/1.

### Step 3: merge all remaining entities

```python
br_3.merge(br_1)
br_3.merge(br_4)

prov_set.generate_provenance()
g_set.commit_changes()

graph_storer.store_graphs_in_file("step3_graph.jsonld")
prov_storer.store_graphs_in_file("step3_prov.jsonld")
```

Now br/3 is the sole surviving entity. The final tree:

<img src="/images/step3.svg" alt="Provenance tree after step 3: br/3 merged with br/1 and br/4, all others deleted" style="background: white; padding: 1rem; border-radius: 8px;" />

## Edge cases

The provenance algorithm handles several scenarios where operations happen between `generate_provenance()` calls.

### Scenario A: creation then merge before any provenance

Entity A is created, then merged with other entities, and only then `generate_provenance()` is called for the first time.

Since no creation snapshot existed before the merge, the algorithm treats A as entirely new. The merge is superseded by the creation: a single creation snapshot is produced.

### Scenario B: merge with entities that have no prior snapshot

Entity A exists and has a creation snapshot. Entities B are created, A is merged with all B entities, and then `generate_provenance()` is called.

The B entities were never registered by provenance, so their deletion cannot be recorded. Without deletion snapshots for the B entities, the algorithm cannot produce a proper merge snapshot for A (which would need to reference those snapshots). Instead, a modification snapshot is generated for A.

### Scenario C: creation then deletion before any provenance

Entity A is created and then deleted before `generate_provenance()` is ever called.

The creation and deletion cancel out. No snapshot is produced for A.

## SnapshotEntity methods

Snapshots are rarely created manually; `generate_provenance()` handles that. But you can read their properties:

```python
for entity in g_set.res_to_entity.values():
    prov_entity = prov_set.get_entity(entity.res + "/prov/se/1")
    if prov_entity:
        print(prov_entity.get_generation_time())
        print(prov_entity.get_is_snapshot_of())
```

Available getters: `get_generation_time()`, `get_invalidation_time()`, `get_is_snapshot_of()`, `get_derives_from()`, `get_primary_source()`.

## Storing provenance

Provenance data is stored separately from graph data. Create a dedicated `Storer` for the `ProvSet`:

```python
prov_storer = Storer(prov_set)
prov_storer.store_graphs_in_file("provenance.jsonld")
prov_storer.upload_all("https://opencitations.net/meta/sparql")
```

## Custom timestamp

By default, `generate_provenance()` uses the current UTC time. To set a specific timestamp, pass a Unix epoch float:

```python
import time
prov_set.generate_provenance(c_time=time.time())
```
