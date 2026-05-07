---
title: Counter handlers
description: Choose a counter strategy for generating unique entity IRIs.
---

When a `GraphSet` creates a new entity, it needs to assign a unique IRI. The IRI is built from the base IRI, the entity type's short name, and a sequential counter. Counter handlers manage these counters.

For example, with a base IRI of `https://w3id.org/oc/meta/` and a counter value of 42, a new `BibliographicResource` receives the IRI `https://w3id.org/oc/meta/br/42`.

## Choosing a handler

The library ships four implementations. Which one to use depends on your environment:

**InMemoryCounterHandler** stores counters in RAM. Counters start at zero on each run and are lost when the process exits. This is the default when no `info_dir` is passed to `GraphSet`. Use it for tests or throwaway scripts where IRI continuity across runs does not matter.

```python
from oc_ocdm.graph import GraphSet

g_set = GraphSet("https://w3id.org/oc/meta/")
```

**FilesystemCounterHandler** persists counters to text files in a directory (one file per entity type). Counters are loaded lazily into RAM and all mutations happen in memory. Changes are written to disk only when you call `flush()` explicitly. If you forget to call it, data is lost; the destructor tries to flush as a safety net, but Python does not guarantee `__del__` will run. This is the default when `info_dir` is provided. Not thread-safe.

```python
g_set = GraphSet("https://w3id.org/oc/meta/", info_dir="/data/counters")

# after all operations
g_set.counter_handler.flush()
```

**SqliteCounterHandler** stores counters in a SQLite database. Each write is committed immediately, so there is no flush step. It is more efficient than `FilesystemCounterHandler` for persistent workflows and easier to set up than Redis. Use it when you need durable counters without the overhead of a separate server.

```python
from oc_ocdm.counter_handler.sqlite_counter_handler import SqliteCounterHandler

handler = SqliteCounterHandler("/data/counters.db")
g_set = GraphSet("https://w3id.org/oc/meta/", custom_counter_handler=handler)
```

**RedisCounterHandler** uses Redis for counter storage. This is the only handler safe for concurrent use from multiple processes or machines: concurrent increments never produce duplicate counters. The constructor accepts `host`, `port`, `db`, and `password` parameters.

```python
from oc_ocdm.counter_handler.redis_counter_handler import RedisCounterHandler

handler = RedisCounterHandler(host="redis.example.com", port=6379, db=0)
g_set = GraphSet("https://w3id.org/oc/meta/", custom_counter_handler=handler)
```

## Supplier prefixes

Supplier prefixes are optional numeric codes that identify the data source within the entity IRI itself. For example, [OpenCitations Meta](https://api.opencitations.net/meta/v1) uses the supplier prefix `060`. An entity with IRI `https://w3id.org/oc/meta/br/0601` encodes the prefix `060` and the counter `1`.

```python
g_set = GraphSet(
    "https://w3id.org/oc/meta/",
    info_dir="/data/counters",
    supplier_prefix="060"
)
```

## Using with ProvSet and MetadataSet

Both `ProvSet` and `MetadataSet` accept the same counter configuration:

```python
from oc_ocdm.prov import ProvSet
from oc_ocdm.metadata import MetadataSet

prov_set = ProvSet(g_set, "https://w3id.org/oc/meta/", info_dir="/data/counters")
meta_set = MetadataSet("https://w3id.org/oc/meta/", info_dir="/data/counters")
```

`ProvSet` also accepts `custom_counter_handler` and `supplier_prefix` parameters. `MetadataSet` uses `FilesystemCounterHandler` when `info_dir` is provided and `InMemoryCounterHandler` otherwise.
