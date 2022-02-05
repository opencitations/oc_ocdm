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

from oc_ocdm.decorators import accepts_only

if TYPE_CHECKING:
    from typing import Optional, List
    from rdflib import URIRef
    from oc_ocdm.graph.entities.bibliographic.reference_pointer import ReferencePointer
    from oc_ocdm.graph.entities.bibliographic.pointer_list import PointerList
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.entities.bibliographic_entity import BibliographicEntity


class DiscourseElement(BibliographicEntity):
    """Discourse element (short: de): a document component, either structural (e.g.
       paragraph, section, chapter, table, caption, footnote, title) or rhetorical (e.g.
       introduction, discussion, acknowledgements, reference list, figure, appendix), in which
       the content of a bibliographic resource can be organized."""

    @accepts_only('de')
    def merge(self, other: DiscourseElement) -> None:
        """
        The merge operation allows combining two ``DiscourseElement`` entities into a single one,
        by marking the second entity as to be deleted while also copying its data into the current
        ``DiscourseElement``. Moreover, every triple from the containing ``GraphSet`` referring to the second
        entity gets "redirected" to the current entity: **every other reference contained inside a
        different source (e.g. a triplestore) must be manually handled by the user!**

        In case of functional properties, values from the current entity get overwritten
        by those coming from the second entity while, in all other cases, values from the
        second entity are simply appended to those of the current entity. In this context,
        ``rdfs:label`` is considered as a functional property, while ``rdf:type`` is not.

        :param other: The entity which will be marked as to be deleted and whose properties will
         be merged into the current entity.
        :type other: DiscourseElement
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        super(DiscourseElement, self).merge(other)

        title: Optional[str] = other.get_title()
        if title is not None:
            self.has_title(title)

        de_list: List[DiscourseElement] = other.get_contained_discourse_elements()
        for cur_de in de_list:
            self.contains_discourse_element(cur_de)

        next_de: Optional[DiscourseElement] = other.get_next_de()
        if next_de is not None:
            self.has_next_de(next_de)

        rp_list: List[ReferencePointer] = other.get_is_context_of_rp()
        for cur_rp in rp_list:
            self.is_context_of_rp(cur_rp)

        pl_list: List[PointerList] = other.get_is_context_of_pl()
        for cur_pl in pl_list:
            self.is_context_of_pl(cur_pl)

        content: Optional[str] = other.get_content()
        if content is not None:
            self.has_content(content)

        number: Optional[str] = other.get_number()
        if number is not None:
            self.has_number(number)

    # HAS TITLE
    def get_title(self) -> Optional[str]:
        """
        Getter method corresponding to the ``dcterms:title`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_title)

    @accepts_only('literal')
    def has_title(self, string: str) -> None:
        """
        Setter method corresponding to the ``dcterms:title`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The title of the discourse element, such as the title of a figure or a section in an article.`

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_title()
        self._create_literal(GraphEntity.iri_title, string)

    def remove_title(self) -> None:
        """
        Remover method corresponding to the ``dcterms:title`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_title, None))
    
    # HAS PART (DiscourseElement)
    def get_contained_discourse_elements(self) -> List[DiscourseElement]:
        """
        Getter method corresponding to the ``frbr:part`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_contains_de, 'de')
        result: List[DiscourseElement] = []
        for uri in uri_list:
            result.append(self.g_set.add_de(self.resp_agent, self.source, uri))
        return result

    @accepts_only('de')
    def contains_discourse_element(self, de_res: DiscourseElement) -> None:
        """
        Setter method corresponding to the ``frbr:part`` RDF predicate.

        `The discourse element hierarchically nested within the parent element, such as a
        sentence within a paragraph, or a paragraph within a section.`

        :param de_res: The value that will be set as the object of the property related to this method
        :type de_res: DiscourseElement
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, GraphEntity.iri_contains_de, de_res.res))

    @accepts_only('de')
    def remove_contained_discourse_element(self, de_res: DiscourseElement = None) -> None:
        """
        Remover method corresponding to the ``frbr:part`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param de_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type de_res: DiscourseElement
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if de_res is not None:
            self.g.remove((self.res, GraphEntity.iri_contains_de, de_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_contains_de, None))

    # HAS NEXT (DiscourseElement)
    def get_next_de(self) -> Optional[DiscourseElement]:
        """
        Getter method corresponding to the ``oco:hasNext`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_has_next, 'de')
        if uri is not None:
            return self.g_set.add_de(self.resp_agent, self.source, uri)

    @accepts_only('de')
    def has_next_de(self, de_res: DiscourseElement) -> None:
        """
        Setter method corresponding to the ``oco:hasNext`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The following discourse element that includes at least one in-text reference pointer.`

        :param de_res: The value that will be set as the object of the property related to this method
        :type de_res: DiscourseElement
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_next_de()
        self.g.add((self.res, GraphEntity.iri_has_next, de_res.res))

    def remove_next_de(self) -> None:
        """
        Remover method corresponding to the ``oco:hasNext`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_next, None))

    # IS CONTEXT OF (ReferencePointer)
    def get_is_context_of_rp(self) -> List[ReferencePointer]:
        """
        Getter method corresponding to the ``c4o:isContextOf`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_is_context_of, 'rp')
        result: List[ReferencePointer] = []
        for uri in uri_list:
            result.append(self.g_set.add_rp(self.resp_agent, self.source, uri))
        return result

    @accepts_only('rp')
    def is_context_of_rp(self, rp_res: ReferencePointer) -> None:
        """
        Setter method corresponding to the ``c4o:isContextOf`` RDF predicate.

        `Provides the textual and semantic context of the in-text reference pointer
        that appears within the discourse element.`

        :param rp_res: The value that will be set as the object of the property related to this method
        :type rp_res: ReferencePointer
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, GraphEntity.iri_is_context_of, rp_res.res))

    @accepts_only('rp')
    def remove_is_context_of_rp(self, rp_res: ReferencePointer = None) -> None:
        """
        Remover method corresponding to the ``c4o:isContextOf`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param rp_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type rp_res: ReferencePointer
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if rp_res is not None:
            self.g.remove((self.res, GraphEntity.iri_is_context_of, rp_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_is_context_of, None))

    # IS CONTEXT OF (PointerList)
    def get_is_context_of_pl(self) -> List[PointerList]:
        """
        Getter method corresponding to the ``c4o:isContextOf`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_is_context_of, 'pl')
        result: List[PointerList] = []
        for uri in uri_list:
            result.append(self.g_set.add_pl(self.resp_agent, self.source, uri))
        return result

    @accepts_only('pl')
    def is_context_of_pl(self, pl_res: PointerList) -> None:
        """
        Setter method corresponding to the ``c4o:isContextOf`` RDF predicate.

        `Provides the textual and semantic context of the list of
        in-text reference pointers that appears within the discourse element.`

        :param pl_res: The value that will be set as the object of the property related to this method
        :type pl_res: PointerList
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, GraphEntity.iri_is_context_of, pl_res.res))

    @accepts_only('pl')
    def remove_is_context_of_pl(self, pl_res: PointerList = None) -> None:
        """
        Remover method corresponding to the ``c4o:isContextOf`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param pl_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type pl_res: PointerList
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if pl_res is not None:
            self.g.remove((self.res, GraphEntity.iri_is_context_of, pl_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_is_context_of, None))

    # HAS CONTENT
    def get_content(self) -> Optional[str]:
        """
        Getter method corresponding to the ``c4o:hasContent`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_has_content)

    @accepts_only('literal')
    def has_content(self, string: str) -> None:
        """
        Setter method corresponding to the ``c4o:hasContent`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The literal document text contained by the discourse element.`

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_content()
        self._create_literal(GraphEntity.iri_has_content, string)

    def remove_content(self) -> None:
        """
        Remover method corresponding to the ``c4o:hasContent`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_content, None))

    # HAS NUMBER
    def get_number(self) -> Optional[str]:
        """
        Getter method corresponding to the ``fabio:hasSequenceIdentifier`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_has_sequence_identifier)

    @accepts_only('literal')
    def has_number(self, string: str) -> None:
        """
        Setter method corresponding to the ``fabio:hasSequenceIdentifier`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_number()
        self._create_literal(GraphEntity.iri_has_sequence_identifier, string)

    def remove_number(self) -> None:
        """
        Remover method corresponding to the ``fabio:hasSequenceIdentifier`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_sequence_identifier, None))

    # HAS TYPE
    @accepts_only('thing')
    def create_discourse_element(self, de_class: URIRef = None) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        If parameter is None, it implicitly sets the object value ``deo:DiscourseElement``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of discourse element – such as “paragraph”, “section”, “sentence”,
        “acknowledgements”, “reference list” or “figure”.`

        :param de_class: The value that will be set as the object of the property related to this method
        :type de_class: URIRef
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if de_class is not None:
            self._create_type(de_class)
        else:
            self._create_type(GraphEntity.iri_discourse_element)

    def create_section(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``doco:Section``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of discourse element – such as “paragraph”, “section”, “sentence”,
        “acknowledgements”, “reference list” or “figure”.`

        :return: None
        """
        self._create_type(GraphEntity.iri_section)

    def create_section_title(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``doco:SectionTitle``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of discourse element – such as “paragraph”, “section”, “sentence”,
        “acknowledgements”, “reference list” or “figure”.`

        :return: None
        """
        self._create_type(GraphEntity.iri_section_title)

    def create_paragraph(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``doco:Paragraph``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of discourse element – such as “paragraph”, “section”, “sentence”,
        “acknowledgements”, “reference list” or “figure”.`

        :return: None
        """
        self._create_type(GraphEntity.iri_paragraph)

    def create_sentence(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``doco:Sentence``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of discourse element – such as “paragraph”, “section”, “sentence”,
        “acknowledgements”, “reference list” or “figure”.`

        :return: None
        """
        self._create_type(GraphEntity.iri_sentence)

    def create_text_chunk(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``doco:TextChunk``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of discourse element – such as “paragraph”, “section”, “sentence”,
        “acknowledgements”, “reference list” or “figure”.`

        :return: None
        """
        self._create_type(GraphEntity.iri_text_chunk)

    def create_table(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``doco:Table``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of discourse element – such as “paragraph”, “section”, “sentence”,
        “acknowledgements”, “reference list” or “figure”.`

        :return: None
        """
        self._create_type(GraphEntity.iri_table)

    def create_footnote(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``doco:Footnote``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of discourse element – such as “paragraph”, “section”, “sentence”,
        “acknowledgements”, “reference list” or “figure”.`

        :return: None
        """
        self._create_type(GraphEntity.iri_footnote)

    def create_caption(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``deo:Caption``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of discourse element – such as “paragraph”, “section”, “sentence”,
        “acknowledgements”, “reference list” or “figure”.`

        :return: None
        """
        self._create_type(GraphEntity.iri_caption)
