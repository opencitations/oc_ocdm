#!/usr/bin/python

# SPDX-FileCopyrightText: 2020-2022 Simone Persiani <iosonopersia@gmail.com>
# SPDX-FileCopyrightText: 2025-2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from triplelite import TripleLite

from oc_ocdm.abstract_entity import AbstractEntity

if TYPE_CHECKING:
    from typing import ClassVar, Dict, List, Optional

E = TypeVar('E', bound=AbstractEntity)


class AbstractSet(ABC, Generic[E]):
    """
    Abstract class which represents a generic set of entities.
    It is the base class for each concrete set of entities.
    """

    short_name_to_type_iri: ClassVar[Dict[str, str]] = {}

    def __init__(self) -> None:
        """
        Constructor of the ``AbstractSet`` class.
        """
        self.res_to_entity: Dict[str, E] = {}

    def graphs(self) -> List[TripleLite]:
        """
        A utility method that allows to retrieve the list of ``TripleLite``
        instances corresponding to each entity contained in the set.

        :return: The requested list of graphs
        """
        result: List[TripleLite] = []
        for entity in self.res_to_entity.values():
            if len(entity.g) > 0:
                result.append(entity.g)
        return result

    def __getstate__(self) -> dict[str, object]:
        """
        Support for pickle serialization.

        RDFLib Graph objects contain threading locks that are not directly picklable,
        but Python's pickle module can handle them. This method provides standard
        pickle protocol support for AbstractSet instances.
        """
        return vars(self).copy()

    def __setstate__(self, state: dict[str, object]) -> None:
        """
        Support for pickle deserialization.

        Restores the AbstractSet state from a pickled representation.
        """
        vars(self).update(state)

    @abstractmethod
    def get_entity(self, res: str) -> Optional[E]:
        """
        Method signature for concrete implementations that allow
        to retrieve a contained entity identified by its URI.

        :param res: The URI that identifies the requested entity
        :type res: URIRef
        :return: The requested entity if found, None otherwise
        """
        raise NotImplementedError

    @staticmethod
    def get_graph_iri(g: TripleLite) -> str:
        """
        A utility method that allows to retrieve the IRI which represents
        the name of a given named graph.

        **NOTE: this is a static function!**

        :param g: The named graph whose name will be returned
        :type g: Graph
        :return: The requested string whose content is the IRI associated to the given named graph
        """
        return str(g.identifier)
