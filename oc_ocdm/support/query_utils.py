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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple
    from rdflib import URIRef
    from oc_ocdm.abstract_entity import AbstractEntity

from rdflib import Graph


def get_delete_query(graph_iri: URIRef, data: Graph) -> Tuple[str, int]:
    num_of_statements: int = len(data)
    if num_of_statements <= 0:
        return "", 0
    else:
        statements: str = data.serialize(format="nt11").replace('\n', '')
        delete_string: str = f"DELETE DATA {{ GRAPH <{graph_iri}> {{ {statements} }} }}"
        return delete_string, num_of_statements


def get_insert_query(graph_iri: URIRef, data: Graph) -> Tuple[str, int]:
    num_of_statements: int = len(data)
    if num_of_statements <= 0:
        return "", 0
    else:
        statements: str = data.serialize(format="nt11").replace('\n', '')
        insert_string: str = f"INSERT DATA {{ GRAPH <{graph_iri}> {{ {statements} }} }}"
        return insert_string, num_of_statements


def _compute_graph_changes(entity: AbstractEntity, entity_type: str) -> Tuple[Graph, Graph, int, int]:
    """
    Computes the triples to insert and delete for an entity.

    Args:
        entity: The entity to analyze
        entity_type: Type of entity ("graph", "prov", or "metadata")

    Returns:
        Tuple of (triples_to_insert, triples_to_delete, added_count, removed_count)
    """
    if entity_type == "prov":
        return entity.g, Graph(), len(entity.g), 0

    to_be_deleted: bool = entity.to_be_deleted
    preexisting_graph: Graph = entity.preexisting_graph

    if to_be_deleted:
        return Graph(), preexisting_graph, 0, len(preexisting_graph)

    preexisting_triples = set(preexisting_graph)
    current_triples = set(entity.g)

    if preexisting_triples == current_triples:
        return Graph(), Graph(), 0, 0

    removed_triples = preexisting_triples - current_triples
    added_triples = current_triples - preexisting_triples

    in_first = Graph()
    for triple in removed_triples:
        in_first.add(triple)

    in_second = Graph()
    for triple in added_triples:
        in_second.add(triple)

    return in_second, in_first, len(in_second), len(in_first)


def serialize_graph_to_nquads(graph: Graph, graph_iri: URIRef) -> list:
    """
    Serializes RDF triples to N-Quads format using rdflib.

    Args:
        graph: RDF graph containing triples
        graph_iri: Named graph IRI

    Returns:
        List of N-Quad strings (each ending with newline)
    """
    nquads = []
    for s, p, o in graph:
        nquad = f"{s.n3()} {p.n3()} {o.n3()} <{graph_iri}> .\n"
        nquads.append(nquad)
    return nquads


def get_separated_queries(entity: AbstractEntity, entity_type: str = "graph") -> Tuple[str, str, int, int, Graph]:
    """
    Returns separate INSERT and DELETE queries for an entity, plus the insert graph.

    Args:
        entity: The entity to generate queries for
        entity_type: Type of entity ("graph", "prov", or "metadata")

    Returns:
        Tuple of (insert_query, delete_query, added_count, removed_count, insert_graph)
        The insert_graph can be used for direct N-Quads serialization without parsing SPARQL.
    """
    to_insert, to_delete, n_added, n_removed = _compute_graph_changes(entity, entity_type)

    if n_added == 0 and n_removed == 0:
        return "", "", 0, 0, Graph()

    delete_string = ""
    insert_string = ""

    if n_removed > 0:
        delete_string, _ = get_delete_query(entity.g.identifier, to_delete)

    if n_added > 0:
        insert_string, _ = get_insert_query(entity.g.identifier, to_insert)

    return insert_string, delete_string, n_added, n_removed, to_insert


def get_update_query(entity: AbstractEntity, entity_type: str = "graph") -> Tuple[str, int, int]:
    to_insert, to_delete, n_added, n_removed = _compute_graph_changes(entity, entity_type)

    if n_added == 0 and n_removed == 0:
        return "", 0, 0

    delete_string, _ = get_delete_query(entity.g.identifier, to_delete)
    insert_string, _ = get_insert_query(entity.g.identifier, to_insert)

    if delete_string != "" and insert_string != "":
        return delete_string + '; ' + insert_string, n_added, n_removed
    elif delete_string != "":
        return delete_string, 0, n_removed
    elif insert_string != "":
        return insert_string, n_added, 0
    else:
        return "", 0, 0