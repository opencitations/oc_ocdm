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

from abc import ABC
from typing import TYPE_CHECKING

from oc_ocdm.support.support import create_type, create_literal
from rdflib import URIRef, RDFS, RDF, Literal, Graph

if TYPE_CHECKING:
    from typing import Optional, List, ClassVar, Dict


class AbstractEntity(ABC):

    short_name_to_type_iri: ClassVar[Dict[str, URIRef]] = {}

    def __init__(self) -> None:
        self.g: Graph = Graph()
        self.res: URIRef = URIRef("")
        self.short_name: str = ""

    def remove_every_triple(self) -> None:
        self.g.remove((None, None, None))

    # LABEL
    def get_label(self) -> Optional[str]:
        return self._get_literal(RDFS.label)

    def create_label(self, string: str) -> None:
        """Creates the RDF triple <self.res> rdfs:label <string>
        inside the graph self.g

        :param string: The string to be added as a label for this entity
        :type string: str
        """
        self.remove_label()
        self._create_literal(RDFS.label, string)

    def remove_label(self) -> None:
        self.g.remove((self.res, RDFS.label, None))

    def _create_literal(self, p: URIRef, s: str, dt: URIRef = None, nor: bool = True) -> None:
        """Creates an RDF triple with a literal object inside the graph self.g

        :param p: The predicate
        :type p: URIRef
        :param s: The string to add as a literal value
        :type s: str
        :param dt: The object's datatype, if present
        :type dt: URIRef, optional
        :param nor: Whether to normalize the graph or not
        :type nor: bool, optional
        """
        create_literal(self.g, self.res, p, s, dt, nor)

    # TYPE
    def get_types(self) -> List[URIRef]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(RDF.type)
        return uri_list

    def _create_type(self, res_type: URIRef) -> None:
        """Creates the RDF triple <self.res> rdf:type <res_type>
        inside the graph self.g

        :param res_type: The RDF class to be associated with this entity
        :type res_type: URIRef
        :rtype: None
        """
        self.remove_type()  # <-- It doesn't remove the main type!
        create_type(self.g, self.res, res_type)

    def remove_type(self) -> None:
        self.g.remove((self.res, RDF.type, None))
        # Restore the main type IRI
        iri_main_type: URIRef = self.short_name_to_type_iri[self.short_name]
        create_type(self.g, self.res, iri_main_type)

    # Overrides __str__ method
    def __str__(self) -> str:
        return str(self.res)

    def add_triples(self, iterable_of_triples) -> None:
        for s, p, o in iterable_of_triples:
            if s == self.res:  # This guarantees that only triples belonging to the resource will be added
                self.g.add((s, p, o))

    def _get_literal(self, predicate: URIRef) -> Optional[str]:
        result: Optional[str] = None
        for o in self.g.objects(self.res, predicate):
            if type(o) == Literal:
                result = str(o)
                break
        return result

    def _get_multiple_literals(self, predicate: URIRef) -> List[str]:
        result: List[str] = []
        for o in self.g.objects(self.res, predicate):
            if type(o) == Literal:
                result.append(str(o))
        return result

    def _get_uri_reference(self, predicate: URIRef) -> Optional[URIRef]:
        result: Optional[URIRef] = None
        for o in self.g.objects(self.res, predicate):
            if type(o) == URIRef:
                result = o
                break
        return result

    def _get_multiple_uri_references(self, predicate: URIRef) -> List[URIRef]:
        result: List[URIRef] = []
        for o in self.g.objects(self.res, predicate):
            if type(o) == URIRef:
                result.append(o)
        return result
