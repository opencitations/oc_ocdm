# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

from typing import TypeAlias, TypedDict

from rdflib import Literal, URIRef
from rdflib.term import Node
from triplelite import Triple

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]
JsonLdDocument: TypeAlias = list[JsonObject]
ContextMap: TypeAlias = dict[str, str | JsonObject]
RdfLibObject: TypeAlias = URIRef | Literal
RdfLibTriple: TypeAlias = tuple[Node, Node, Node]
RdfLibQuad: TypeAlias = tuple[URIRef, URIRef, RdfLibObject, URIRef | None]
SparqlBinding: TypeAlias = dict[str, str]
SparqlResultRow: TypeAlias = dict[str, SparqlBinding]
SparqlResultRows: TypeAlias = list[SparqlResultRow]
TripleSet: TypeAlias = set[Triple]
FrozenTripleSet: TypeAlias = frozenset[Triple]


class SparqlResults(TypedDict):
    bindings: SparqlResultRows


class SparqlQueryResult(TypedDict):
    results: SparqlResults
