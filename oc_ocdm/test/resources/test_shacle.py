import os
import unittest

from pyshacl import validate
from rdflib import ConjunctiveGraph, Graph, URIRef

from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.reader import Reader


class TestShacle(unittest.TestCase):
    def test_validate(self):
      data_graph = ConjunctiveGraph()
      sg = Graph()
      data_graph.parse(source=os.path.join('oc_ocdm', 'test', 'resources', 'data.json'), format='json-ld')
      sg.parse(source=os.path.join('oc_ocdm', 'resources', 'shacle.ttl'), format='text/turtle')
      r = validate(data_graph,
        shacl_graph=sg,
        ont_graph=None,
        inference=None,
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
        meta_shacl=False,
        advanced=False,
        js=False,
        debug=False)
      conforms, _, _ = r
      self.assertEqual(conforms, True)
    
    def test_reader(self):
      reader = Reader()
      g_set = GraphSet(base_iri='https://w3id.org/oc/meta/')
      g = ConjunctiveGraph()
      g.parse(source=os.path.join('oc_ocdm', 'test', 'resources', 'data_reader.json'))
      results = []
      for triple in g:
        o = triple[2]
        o_type = 'uri' if isinstance(o, URIRef) else 'literal'
        if o_type == 'literal' and o.datatype:
          results.append({'s': {'type': 'uri', 'value': str(triple[0])}, 'p': {'type': 'uri', 'value': str(triple[1])}, 'o': {'type': o_type, 'value': str(triple[2]), 'datatype': str(o.datatype)}})
        else:
          results.append({'s': {'type': 'uri', 'value': str(triple[0])}, 'p': {'type': 'uri', 'value': str(triple[1])}, 'o': {'type': o_type, 'value': str(triple[2])}})
      reader.import_entities_from_graph(g_set, results, resp_agent='https://orcid.org/0000-0002-8420-0696', enable_validation=True, closed=False)
      self.assertEqual(set(str(s) for s in g_set.res_to_entity.keys()), {
         'https://w3id.org/oc/meta/br/060209',
         'https://w3id.org/oc/meta/br/060182', 
         'https://w3id.org/oc/meta/ar/06034124', 
         'https://w3id.org/oc/meta/ra/06099', 
         'https://w3id.org/oc/meta/ar/060128', 
         'https://w3id.org/oc/meta/id/060313', 
         'https://w3id.org/oc/meta/ra/06098', 
         'https://w3id.org/oc/meta/re/06011'})

    def test_reader_invalid(self):
      reader = Reader()
      g_set = GraphSet(base_iri='https://w3id.org/oc/meta/')
      g = ConjunctiveGraph()
      g.parse(source=os.path.join('oc_ocdm', 'test', 'resources', 'data_reader_invalid.json'))
      results = []
      for triple in g:
        o = triple[2]
        o_type = 'uri' if isinstance(o, URIRef) else 'literal'
        if o_type == 'literal' and o.datatype:
          results.append({'s': {'type': 'uri', 'value': str(triple[0])}, 'p': {'type': 'uri', 'value': str(triple[1])}, 'o': {'type': o_type, 'value': str(triple[2]), 'datatype': str(o.datatype)}})
        else:
          results.append({'s': {'type': 'uri', 'value': str(triple[0])}, 'p': {'type': 'uri', 'value': str(triple[1])}, 'o': {'type': o_type, 'value': str(triple[2])}})
      reader.import_entities_from_graph(g_set, results, resp_agent='https://orcid.org/0000-0002-8420-0696', enable_validation=True, closed=False)
      self.assertEqual(set(str(s) for s in g_set.res_to_entity.keys()), {
         'https://w3id.org/oc/meta/br/060182', 
         'https://w3id.org/oc/meta/ar/06034124', 
         'https://w3id.org/oc/meta/ra/06099', 
         'https://w3id.org/oc/meta/ar/060128', 
         'https://w3id.org/oc/meta/id/060313', 
         'https://w3id.org/oc/meta/ra/06098', 
         'https://w3id.org/oc/meta/re/06011'})