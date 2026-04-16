# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

import json
import os


def _load_context() -> dict:
    context_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "metadata", "context.json"
    )
    with open(context_path, "rt", encoding="utf-8") as f:
        return json.load(f)


CONTEXT: dict = _load_context()


class Namespace:
    __slots__ = ("_base",)

    def __init__(self, base: str) -> None:
        self._base = base

    def __getattr__(self, name: str) -> str:
        if name.startswith("_"):
            raise AttributeError(name)
        return self._base + name

    def __getitem__(self, name: str) -> str:
        return self._base + name


_XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"

XSD_STRING = _XSD.string
XSD_DATE = _XSD.date
XSD_DATETIME = _XSD.dateTime
XSD_DURATION = _XSD.duration
XSD_DECIMAL = _XSD.decimal
XSD_GYEAR = _XSD.gYear
XSD_GYEARMONTH = _XSD.gYearMonth
