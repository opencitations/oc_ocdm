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
    from typing import Optional, Tuple
    from rdflib import URIRef
    from rdflib.compare import IsomorphicGraph
    from oc_ocdm.abstract_entity import AbstractEntity

from rdflib import Graph
from rdflib.compare import to_isomorphic, graph_diff


def get_delete_query(graph_iri: URIRef, data: Graph) -> Optional[str]:
    if len(data) == 0:
        return None
    delete_string: str = f"DELETE DATA {{ GRAPH <{graph_iri}> {{ "
    delete_string += data.serialize(format="nt11", encoding="utf-8").decode("utf-8")
    return delete_string.replace('\n\n', '') + "} }"


def get_insert_query(graph_iri: URIRef, data: Graph) -> Optional[str]:
    if len(data) == 0:
        return None
    insert_string: str = f"INSERT DATA {{ GRAPH <{graph_iri}> {{ "
    insert_string += data.serialize(format="nt11", encoding="utf-8").decode("utf-8")
    return insert_string.replace('\n\n', '') + "} }"


def get_update_query(entity: AbstractEntity, entity_type: str = "graph") -> Tuple[str, int, int]:
    if entity_type in ["graph", "metadata"]:
        to_be_deleted: bool = entity.to_be_deleted
        preexisting_graph: Graph = entity.preexisting_graph
    elif entity_type == "prov":
        to_be_deleted: bool = False
        preexisting_graph: Graph = Graph(identifier=entity.g.identifier)

    if to_be_deleted:
        removed_triples: int = len(entity.g)
        return get_delete_query(entity.g.identifier, preexisting_graph), 0, removed_triples
    else:
        preexisting_iso: IsomorphicGraph = to_isomorphic(preexisting_graph)
        current_iso: IsomorphicGraph = to_isomorphic(entity.g)
        if preexisting_iso == current_iso:
            # Both graphs have exactly the same content!
            return "", 0, 0
        in_both, in_first, in_second = graph_diff(preexisting_iso, current_iso)
        delete_string: Optional[str] = get_delete_query(entity.g.identifier, in_first)
        insert_string: Optional[str] = get_insert_query(entity.g.identifier, in_second)

        removed_triples: int = len(in_first)
        added_triples: int = len(in_second)

        if delete_string is not None and insert_string is not None:
            return delete_string + ' ' + insert_string, added_triples, removed_triples
        elif delete_string is not None:
            return delete_string, 0, removed_triples
        elif insert_string is not None:
            return insert_string, added_triples, 0
        else:
            return "", 0, 0
