#!/usr/bin/python

# SPDX-FileCopyrightText: 2020-2022 Simone Persiani <iosonopersia@gmail.com>
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from triplelite import TripleLite

from oc_ocdm.constants import RDF_TYPE, RDFS_LABEL
from oc_ocdm.support.support import create_literal, create_type, get_short_name, is_dataset, is_string_empty

if TYPE_CHECKING:
    from typing import ClassVar, Dict, List, Optional


class AbstractEntity(ABC):
    """
    Abstract class which represents a generic entity from the OCDM. It sits
    at the top of the entity class hierarchy.
    """

    short_name_to_type_iri: ClassVar[Dict[str, str]] = {}

    def __init__(self) -> None:
        self.g: TripleLite = TripleLite()
        self.res: str = ""
        self.short_name: str = ""

    def remove_every_triple(self) -> None:
        """
        Remover method that removes every triple from the current entity.

        **WARNING: the OCDM specification requires that every entity has at least
        one triple that defines its type (through the** ``rdf:type`` **RDF predicate). If
        such triple is not subsequently restored by the user, the entity will be considered
        as to be deleted since it wouldn't be valid anymore.**

        :return: None
        """
        self.g.remove((None, None, None))  # type: ignore[arg-type]

    # LABEL
    def get_label(self) -> Optional[str]:
        """
        Getter method corresponding to the ``rdfs:label`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(RDFS_LABEL)

    def create_label(self, string: str) -> None:
        """
        Setter method corresponding to the ``rdfs:label`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :return: None
        """
        self.remove_label()
        self._create_literal(RDFS_LABEL, string)

    def remove_label(self) -> None:
        """
        Remover method corresponding to the ``rdfs:label`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, RDFS_LABEL, None))

    def _create_literal(self, p: str, s: str, dt: str | None = None, nor: bool = True) -> None:
        """
        Adds an RDF triple with a literal object inside the graph of the entity

        :param p: The predicate
        :type p: str
        :param s: The string to add as a literal value
        :type s: str
        :param dt: The object's datatype, if present
        :type dt: str, optional
        :param nor: Whether to normalize the graph or not
        :type nor: bool, optional
        :return: None
        """
        create_literal(self.g, self.res, p, s, dt, nor)

    # TYPE
    def get_types(self) -> List[str]:
        """
        Getter method corresponding to the ``rdf:type`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[str] = self._get_multiple_uri_references(RDF_TYPE)
        return uri_list

    def _create_type(self, res_type: str) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        :param res_type: The value that will be set as the object of the property related to this method
        :type res_type: str
        :return: None
        """
        self.remove_type()  # <-- It doesn't remove the main type!
        create_type(self.g, self.res, res_type)

    def remove_type(self) -> None:
        """
        Remover method corresponding to the ``rdf:type`` RDF predicate.

        **WARNING: the OCDM specification requires at least one type for an entity.
        This method removes any existing secondary type, without removing the main type.**

        :return: None
        """
        self.g.remove((self.res, RDF_TYPE, None))
        # Restore the main type IRI
        iri_main_type: str = self.short_name_to_type_iri[self.short_name]
        create_type(self.g, self.res, iri_main_type)

    # Overrides __str__ method
    def __str__(self) -> str:
        return str(self.res)

    def _get_literal(self, predicate: str) -> Optional[str]:
        for o in self.g.objects(self.res, predicate):
            if o.type == "literal":
                return o.value
        return None

    def _get_multiple_literals(self, predicate: str) -> List[str]:
        result: List[str] = []
        for o in self.g.objects(self.res, predicate):
            if o.type == "literal":
                result.append(o.value)
        return result

    def _get_uri_reference(self, predicate: str, short_name: Optional[str] = None) -> Optional[str]:
        for o in self.g.objects(self.res, predicate):
            if o.type != "uri":
                continue
            uri = o.value
            if not is_string_empty(short_name):
                if (short_name == '_dataset_' and is_dataset(uri)) or get_short_name(uri) == short_name:
                    return uri
            else:
                return uri
        return None

    def _get_multiple_uri_references(self, predicate: str, short_name: Optional[str] = None) -> List[str]:
        result: List[str] = []
        for o in self.g.objects(self.res, predicate):
            if o.type != "uri":
                continue
            uri = o.value
            if not is_string_empty(short_name):
                if (short_name == '_dataset_' and is_dataset(uri)) or get_short_name(uri) == short_name:
                    result.append(uri)
            else:
                result.append(uri)
        return result
