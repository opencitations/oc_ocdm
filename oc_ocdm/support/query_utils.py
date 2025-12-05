#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2016, Silvio Peroni <essepuntato@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.
from __future__ import annotations

from typing import TYPE_CHECKING, List, Set

if TYPE_CHECKING:
    from typing import Tuple
    from rdflib import URIRef
    from oc_ocdm.abstract_entity import AbstractEntity

MAX_TRIPLES_PER_QUERY = 500


def _serialize_triples_to_nt(triples: Set) -> str:
    return "".join(f"{s.n3()} {p.n3()} {o.n3()} ." for s, p, o in triples)


def _chunk_set(data: Set, chunk_size: int) -> List[Set]:
    data_list = list(data)
    return [set(data_list[i:i + chunk_size]) for i in range(0, len(data_list), chunk_size)]


def get_delete_query(graph_iri: URIRef, data: Set) -> Tuple[List[str], int]:
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


def get_insert_query(graph_iri: URIRef, data: Set) -> Tuple[List[str], int]:
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


def _compute_graph_changes(entity: AbstractEntity, entity_type: str) -> Tuple[Set, Set, int, int]:
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

    to_be_deleted: bool = entity.to_be_deleted
    preexisting_graph = entity.preexisting_graph

    if to_be_deleted:
        preexisting_triples = set(preexisting_graph)
        return set(), preexisting_triples, 0, len(preexisting_triples)

    preexisting_triples = set(preexisting_graph)
    current_triples = set(entity.g)

    if preexisting_triples == current_triples:
        return set(), set(), 0, 0

    removed_triples = preexisting_triples - current_triples
    added_triples = current_triples - preexisting_triples

    return added_triples, removed_triples, len(added_triples), len(removed_triples)


def serialize_graph_to_nquads(triples: Set, graph_iri: URIRef) -> list:
    """
    Serializes RDF triples to N-Quads format.

    Args:
        triples: Set of RDF triples
        graph_iri: Named graph IRI

    Returns:
        List of N-Quad strings (each ending with newline)
    """
    return [f"{s.n3()} {p.n3()} {o.n3()} <{graph_iri}> .\n" for s, p, o in triples]


def get_separated_queries(entity: AbstractEntity, entity_type: str = "graph") -> Tuple[List[str], List[str], int, int, Set]:
    """
    Returns separate INSERT and DELETE queries for an entity, plus the insert triples.

    Args:
        entity: The entity to generate queries for
        entity_type: Type of entity ("graph", "prov", or "metadata")

    Returns:
        Tuple of (insert_queries, delete_queries, added_count, removed_count, insert_triples)
        The insert_triples can be used for direct N-Quads serialization without parsing SPARQL.
    """
    to_insert, to_delete, n_added, n_removed = _compute_graph_changes(entity, entity_type)

    if n_added == 0 and n_removed == 0:
        return [], [], 0, 0, set()

    delete_queries = []
    insert_queries = []

    if n_removed > 0:
        delete_queries, _ = get_delete_query(entity.g.identifier, to_delete)

    if n_added > 0:
        insert_queries, _ = get_insert_query(entity.g.identifier, to_insert)

    return insert_queries, delete_queries, n_added, n_removed, to_insert


def get_update_query(entity: AbstractEntity, entity_type: str = "graph") -> Tuple[List[str], int, int]:
    to_insert, to_delete, n_added, n_removed = _compute_graph_changes(entity, entity_type)

    if n_added == 0 and n_removed == 0:
        return [], 0, 0

    delete_queries, _ = get_delete_query(entity.g.identifier, to_delete)
    insert_queries, _ = get_insert_query(entity.g.identifier, to_insert)

    return delete_queries + insert_queries, n_added, n_removed
