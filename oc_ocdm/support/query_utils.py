#!/usr/bin/python

# SPDX-FileCopyrightText: 2020-2022 Simone Persiani <iosonopersia@gmail.com>
# SPDX-FileCopyrightText: 2023-2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING, AbstractSet, List, Set

from oc_ocdm.light_graph import RDFTerm

if TYPE_CHECKING:
    from typing import Tuple

    from oc_ocdm.abstract_entity import AbstractEntity

MAX_TRIPLES_PER_QUERY = 500


def _term_to_nt(term) -> str:
    if isinstance(term, RDFTerm):
        if term.type == "literal":
            escaped = term.value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
            if term.lang:
                return f'"{escaped}"@{term.lang}'
            return f'"{escaped}"^^<{term.datatype}>'
        return f'<{term.value}>'
    if isinstance(term, str):
        return f'<{term}>'
    return term.n3()


def _serialize_triples_to_nt(triples: AbstractSet) -> str:
    return "".join(f"{_term_to_nt(s)} {_term_to_nt(p)} {_term_to_nt(o)} ." for s, p, o in triples)


def _chunk_set(data: AbstractSet, chunk_size: int) -> List[Set]:
    data_list = list(data)
    return [set(data_list[i:i + chunk_size]) for i in range(0, len(data_list), chunk_size)]


def get_delete_query(graph_iri: str, data: AbstractSet) -> Tuple[List[str], int]:
    num_of_statements: int = len(data)
    if num_of_statements <= 0:
        return [], 0

    if num_of_statements <= MAX_TRIPLES_PER_QUERY:
        statements: str = _serialize_triples_to_nt(data)
        return [f"DELETE DATA {{ GRAPH <{graph_iri}> {{ {statements} }} }}"], num_of_statements

    chunks = _chunk_set(data, MAX_TRIPLES_PER_QUERY)
    queries = []
    for chunk in chunks:
        statements = _serialize_triples_to_nt(chunk)
        queries.append(f"DELETE DATA {{ GRAPH <{graph_iri}> {{ {statements} }} }}")
    return queries, num_of_statements


def get_insert_query(graph_iri: str, data: AbstractSet) -> Tuple[List[str], int]:
    num_of_statements: int = len(data)
    if num_of_statements <= 0:
        return [], 0

    if num_of_statements <= MAX_TRIPLES_PER_QUERY:
        statements: str = _serialize_triples_to_nt(data)
        return [f"INSERT DATA {{ GRAPH <{graph_iri}> {{ {statements} }} }}"], num_of_statements

    chunks = _chunk_set(data, MAX_TRIPLES_PER_QUERY)
    queries = []
    for chunk in chunks:
        statements = _serialize_triples_to_nt(chunk)
        queries.append(f"INSERT DATA {{ GRAPH <{graph_iri}> {{ {statements} }} }}")
    return queries, num_of_statements


def _compute_graph_changes(entity: AbstractEntity, entity_type: str) -> Tuple[AbstractSet, AbstractSet, int, int]:
    """
    Computes the triples to insert and delete for an entity.

    Args:
        entity: The entity to analyze
        entity_type: Type of entity ("graph", "prov", or "metadata")

    Returns:
        Tuple of (triples_to_insert, triples_to_delete, added_count, removed_count)
    """
    if entity_type == "prov":
        triples = set(entity.g)
        return triples, set(), len(triples), 0

    # Deferred import to break circular dependency:
    # graph_entity → abstract_entity → support.support → (support/__init__) → query_utils → graph_entity
    from oc_ocdm.graph.graph_entity import GraphEntity  # noqa: E402

    assert isinstance(entity, GraphEntity)
    to_be_deleted: bool = entity.to_be_deleted
    preexisting_triples = entity._preexisting_triples

    if to_be_deleted:
        return set(), set(preexisting_triples), 0, len(preexisting_triples)

    current_triples = set(entity.g)

    if len(preexisting_triples) == len(current_triples) and preexisting_triples == current_triples:
        return set(), set(), 0, 0

    removed_triples = preexisting_triples - current_triples
    added_triples = current_triples - preexisting_triples

    return added_triples, removed_triples, len(added_triples), len(removed_triples)


def get_update_query(entity: AbstractEntity, entity_type: str = "graph") -> Tuple[List[str], int, int]:
    to_insert, to_delete, n_added, n_removed = _compute_graph_changes(entity, entity_type)

    if n_added == 0 and n_removed == 0:
        return [], 0, 0

    graph_iri = entity.g.identifier
    if graph_iri is None:
        raise ValueError("Entity graph has no identifier")

    delete_queries, _ = get_delete_query(graph_iri, to_delete)
    insert_queries, _ = get_insert_query(graph_iri, to_insert)

    return delete_queries + insert_queries, n_added, n_removed
