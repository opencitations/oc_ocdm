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
from rdflib import URIRef

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from oc_graphlib.bibliographic_resource import BibliographicResource
from oc_graphlib.prov_entity import GraphEntity
from oc_graphlib.bibliographic_entity import BibliographicEntity

"""
Notes about CI:
    
    HAS CITATION CREATION DATE is missing!
    HAS CITATION TIME SPAN is missing!
    HAS CITATION CHARACTERIZATION is missing!
"""


class Citation(BibliographicEntity):

    # HAS CITING DOCUMENT (BibliographicResource)
    # HAS CITED DOCUMENT (BibliographicResource)
    # <self.res> CITO:hasCitingEntity <citing_res>
    # <self.res> CITO:hasCitedEntity <cited_res>
    def _create_citation(self, citing_res: BibliographicResource, cited_res: BibliographicResource) -> None:
        self.g.add((self.res, GraphEntity.has_citing_entity, URIRef(str(citing_res))))
        self.g.add((self.res, GraphEntity.has_cited_entity, URIRef(str(cited_res))))