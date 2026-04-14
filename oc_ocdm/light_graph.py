# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

from typing import Iterator, NamedTuple

from rdflib import Literal, URIRef

_XSD_STRING = "http://www.w3.org/2001/XMLSchema#string"


class RDFTerm(NamedTuple):
    type: str
    value: str
    datatype: str = ""
    lang: str = ""


def rdflib_to_rdfterm(o) -> RDFTerm:
    if isinstance(o, RDFTerm):
        return o
    if hasattr(o, "datatype"):
        dt = str(o.datatype) if o.datatype else _XSD_STRING
        lang = str(o.language) if hasattr(o, "language") and o.language else ""
        return RDFTerm("literal", str(o), dt, lang)
    return RDFTerm("uri", str(o))


Triple = tuple[str, str, RDFTerm]
SPOIndex = dict[str, dict[str, set[RDFTerm]]]


class LightGraph:
    __slots__ = ("_spo", "_triples", "identifier")

    def __init__(self, identifier: str | None = None) -> None:
        self._spo: SPOIndex = {}
        self._triples: set[Triple] = set()
        self.identifier: str | None = identifier

    def add(self, triple: tuple[str, str, RDFTerm]) -> None:
        s, p, o = str(triple[0]), str(triple[1]), triple[2]
        t = (s, p, o)
        if t in self._triples:
            return
        self._triples.add(t)
        self._spo.setdefault(s, {}).setdefault(p, set()).add(o)

    def remove(self, triple: tuple[str | None, str | None, RDFTerm | None]) -> None:
        s, p, o = triple
        if s is None and p is None and o is None:
            self._spo.clear()
            self._triples.clear()
            return
        s_str = str(s) if s is not None else None
        p_str = str(p) if p is not None else None
        o_cmp = o
        to_remove: list[Triple] = []
        if s_str is not None and p_str is not None and o_cmp is not None:
            t = (s_str, p_str, o_cmp)
            if t in self._triples:
                to_remove.append(t)
        elif s_str is not None:
            pred_dict = self._spo.get(s_str, {})
            if p_str is not None:
                for obj in list(pred_dict.get(p_str, set())):
                    if o_cmp is None or obj == o_cmp:
                        to_remove.append((s_str, p_str, obj))
            else:
                for pred, objs in pred_dict.items():
                    for obj in list(objs):
                        if o_cmp is None or obj == o_cmp:
                            to_remove.append((s_str, pred, obj))
        else:
            for t in list(self._triples):
                if (p_str is None or t[1] == p_str) and (o_cmp is None or t[2] == o_cmp):
                    to_remove.append(t)
        for ts, tp, to in to_remove:
            self._triples.discard((ts, tp, to))
            pred_dict = self._spo.get(ts)
            if pred_dict is not None:
                obj_set = pred_dict.get(tp)
                if obj_set is not None:
                    obj_set.discard(to)
                    if not obj_set:
                        del pred_dict[tp]
                if not pred_dict:
                    del self._spo[ts]

    def triples(self, pattern: tuple[str | None, str | None, RDFTerm | None]) -> Iterator[Triple]:
        s, p, o = pattern
        s_str = str(s) if s is not None else None
        p_str = str(p) if p is not None else None
        o_cmp = o
        if s_str is not None:
            pred_dict = self._spo.get(s_str)
            if pred_dict is None:
                return
            if p_str is not None:
                obj_set = pred_dict.get(p_str)
                if obj_set is None:
                    return
                for obj in obj_set:
                    if o_cmp is None or obj == o_cmp:
                        yield s_str, p_str, obj
            else:
                for pred, objs in pred_dict.items():
                    for obj in objs:
                        if o_cmp is None or obj == o_cmp:
                            yield s_str, pred, obj
        else:
            for t in self._triples:
                if (p_str is None or t[1] == p_str) and (o_cmp is None or t[2] == o_cmp):
                    yield t

    def objects(self, subject=None, predicate=None) -> Iterator[RDFTerm]:
        s_str = str(subject) if subject is not None else None
        p_str = str(predicate) if predicate is not None else None
        if s_str is not None and p_str is not None:
            yield from self._spo.get(s_str, {}).get(p_str, set())
            return
        if s_str is not None:
            for objs in self._spo.get(s_str, {}).values():
                yield from objs
            return
        for t in self._triples:
            if p_str is None or t[1] == p_str:
                yield t[2]

    def predicate_objects(self, subject=None, **_kwargs) -> Iterator[tuple[str, RDFTerm]]:
        s_str = str(subject) if subject is not None else None
        if s_str is not None:
            for pred, objs in self._spo.get(s_str, {}).items():
                for obj in objs:
                    yield pred, obj
            return
        for t in self._triples:
            yield t[1], t[2]

    def __contains__(self, triple: tuple[str, str, RDFTerm]) -> bool:
        s, p, o = triple
        return (str(s), str(p), o) in self._triples

    def __iter__(self) -> Iterator[Triple]:
        return iter(self._triples)

    def __len__(self) -> int:
        return len(self._triples)

    def to_rdflib_quads(self):
        graph_id = URIRef(self.identifier) if self.identifier else None
        for s, p, o in self._triples:
            s_ref = URIRef(s)
            p_ref = URIRef(p)
            if o.type == "literal":
                if o.lang:
                    o_ref = Literal(o.value, lang=o.lang)
                else:
                    o_ref = Literal(o.value, datatype=URIRef(o.datatype))
            else:
                o_ref = URIRef(o.value)
            yield s_ref, p_ref, o_ref, graph_id
