#!/usr/bin/python
# Copyright (c) 2004-2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# - Anahide Tchertchian <at@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
#-------------------------------------------------------------------------------
# $Id$
"""Test RDF Graph
"""

from Products.CPSRelation.tests.CPSRelationTestCase import USE_RDF

import os, sys
if __name__ == '__main__' and USE_RDF:
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Interface.Verify import verifyClass

if USE_RDF:
    from rdflib import Graph as rdflibGraph
    from rdflib import URIRef
    from Products.CPSRelation.interfaces.IGraph import IGraph
    from Products.CPSRelation.rdfgraph import RDFGraph
    from Products.CPSRelation.tests.CPSRelationTestCase import RDFGraphTestCase
    from Products.CPSRelation.tests.CPSRelationTestCase import RDF_NAMESPACE
else:
    class RDFGraphTestCase:
        pass

class TestRDFGraph(RDFGraphTestCase):

    def test_interface(self):
        verifyClass(IGraph, RDFGraph)

    def test_creation(self):
        bindings = {
            "dc": "http://purl.org/dc/elements/1.1/",
            "dc2": "http://purl.org/dc/elements/1.1/",
            }
        dummy = RDFGraph('dummy', bindings=bindings)
        self.assertEqual(dummy.getId(), 'dummy')
        self.assertEqual(dummy.meta_type, 'RDF Graph')

    def test_test_case_graph(self):
        self.assertEqual(self.graph.getId(), 'rdfgraph')
        self.assertEqual(self.graph.meta_type, 'RDF Graph')
        self.assert_(isinstance(self.graph, RDFGraph))
        self.assert_(self.hasPart_ns,
                     u'http://cps-project.org/2005/data/hasPart')
        self.assert_(self.isPartOf_ns,
                     u'http://cps-project.org/2005/data/isPartOf')

    def test__getRDFGraph(self):
        self.assert_(isinstance(self.graph._getRDFGraph(), rdflibGraph))

    def test_parse_file(self):
        test_graph = RDFGraph('dummy')
        from Products.CPSRelation import tests as here_tests
        input_source = os.path.join(here_tests.__path__[0],
                                    'test_files/rdf_graph.xml')
        test_graph.parse(input_source, publicID='Dummy publicID')
        all_relations = [
            (URIRef('1'), self.hasPart_ns, URIRef('10')),
            (URIRef('2'), self.hasPart_ns, URIRef('10')),
            (URIRef('2'), self.hasPart_ns, URIRef('23')),
            (URIRef('2'), self.hasPart_ns, URIRef('25')),
            (URIRef('10'), self.isPartOf_ns, URIRef('1')),
            (URIRef('10'), self.isPartOf_ns, URIRef('2')),
            (URIRef('23'), self.isPartOf_ns, URIRef('2')),
            (URIRef('25'), self.isPartOf_ns, URIRef('2')),
            ]
        self.assertEqual(test_graph.listAllRelations(), all_relations)

    def test_parse_string(self):
        test_graph = RDFGraph('dummy')
        input_source = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns:_3="http://cps-project.org/2005/data/"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
   xmlns:xml="http://www.w3.org/XML/1998/namespace"
>
  <rdf:Description rdf:about="2">
    <_3:hasPart rdf:resource="25"/>
    <_3:hasPart rdf:resource="23"/>
    <_3:hasPart rdf:resource="10"/>
  </rdf:Description>
  <rdf:Description rdf:about="25">
    <_3:isPartOf rdf:resource="2"/>
  </rdf:Description>
  <rdf:Description rdf:about="23">
    <_3:isPartOf rdf:resource="2"/>
  </rdf:Description>
  <rdf:Description rdf:about="10">
    <_3:isPartOf rdf:resource="2"/>
    <_3:isPartOf rdf:resource="1"/>
  </rdf:Description>
  <rdf:Description rdf:about="1">
    <_3:hasPart rdf:resource="10"/>
  </rdf:Description>
</rdf:RDF>
"""
        test_graph.parse(input_source)
        all_relations = [
            (URIRef('1'), self.hasPart_ns, URIRef('10')),
            (URIRef('2'), self.hasPart_ns, URIRef('10')),
            (URIRef('2'), self.hasPart_ns, URIRef('23')),
            (URIRef('2'), self.hasPart_ns, URIRef('25')),
            (URIRef('10'), self.isPartOf_ns, URIRef('1')),
            (URIRef('10'), self.isPartOf_ns, URIRef('2')),
            (URIRef('23'), self.isPartOf_ns, URIRef('2')),
            (URIRef('25'), self.isPartOf_ns, URIRef('2')),
            ]
        self.assertEqual(test_graph.listAllRelations(), all_relations)

    def test_serialize(self):
        serialized = self.graph.serialize()
        # not possible to test xml rendering, it changes every time...
        start = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns:_3="http://cps-project.org/2005/data/"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
   xmlns:xml="http://www.w3.org/XML/1998/namespace"
>"""
        self.assert_(serialized.startswith(start))
        end = "</rdf:RDF>\n"
        self.assert_(serialized.endswith(end))

    def test_listRelationIds(self):
        self.assertEqual(self.graph.listRelationIds(),
                         [self.isPartOf_ns, self.hasPart_ns])

    def test_deleteAllRelations(self):
        self.assertEqual(self.graph.listRelationIds(),
                         [self.isPartOf_ns, self.hasPart_ns])
        self.graph.deleteAllRelations()
        self.assertEqual(self.graph.listRelationIds(), [])

    def test_hasRelation(self):
        self.assertEqual(self.graph.hasRelation(self.isPartOf_ns),
                         True)


        self.assertEqual(self.graph.hasRelation(RDF_NAMESPACE['isPartOfEuh']),
                         False)

    def test_addRelation(self):
        self.assertEqual(self.graph.listRelationIds(),
                         [self.isPartOf_ns, self.hasPart_ns])
        new_relation = RDF_NAMESPACE['dummy']
        self.graph.addRelation(new_relation)
        self.assertEqual(self.graph.listRelationIds(),
                         [self.isPartOf_ns, self.hasPart_ns])
        # XXX AT: in RDF graph, relation is added only if a relation instance
        # is added...
        self.graph.addRelationFor(URIRef('25'), new_relation, URIRef('2'))
        self.assertEqual(self.graph.listRelationIds(),
                         [self.isPartOf_ns, new_relation, self.hasPart_ns])

    def test_deleteRelation(self):
        self.assertEqual(self.graph.listRelationIds(),
                         [self.isPartOf_ns, self.hasPart_ns])
        self.graph.deleteRelation(self.isPartOf_ns)
        self.assertEqual(self.graph.listRelationIds(),
                         [self.hasPart_ns])

    def test_listAllRelations(self):
        all_relations = [
            (URIRef('1'), self.hasPart_ns, URIRef('10')),
            (URIRef('2'), self.hasPart_ns, URIRef('10')),
            (URIRef('2'), self.hasPart_ns, URIRef('23')),
            (URIRef('2'), self.hasPart_ns, URIRef('25')),
            (URIRef('10'), self.isPartOf_ns, URIRef('1')),
            (URIRef('10'), self.isPartOf_ns, URIRef('2')),
            (URIRef('23'), self.isPartOf_ns, URIRef('2')),
            (URIRef('25'), self.isPartOf_ns, URIRef('2')),
            ]
        self.assertEqual(self.graph.listAllRelations(), all_relations)

    def test_hasRelationFor(self):
        self.assertEqual(
            self.graph.hasRelationFor(URIRef('1'), self.hasPart_ns),
            True)
        self.assertEqual(
            self.graph.hasRelationFor(URIRef('3'), self.hasPart_ns),
            False)

    def test_addRelationFor(self):
        self.assertEqual(
            self.graph.hasRelationFor(URIRef('3'), self.hasPart_ns),
            False)
        self.graph.addRelationFor(URIRef('3'), self.hasPart_ns, URIRef('10'))
        self.assertEqual(
            self.graph.hasRelationFor(URIRef('3'), self.hasPart_ns),
            True)

    def test_deleteRelationFor(self):
        self.assertEqual(
            self.graph.getRelationsFor(URIRef('1'), self.hasPart_ns),
            (URIRef('10'),))
        self.graph.deleteRelationFor(URIRef('1'), self.hasPart_ns, URIRef('10'))
        self.assertEqual(
            self.graph.getRelationsFor(URIRef('1'), self.hasPart_ns),
            ())

    def test_getValueFor(self):
        # 1 --hasPart--> 10
        # 2 --hasPart--> 10, 23, 25
        self.assertEqual(
            self.graph.getValueFor(URIRef('1'), self.hasPart_ns),
            URIRef('10'))
        # test default
        self.assertEqual(
            self.graph.getValueFor(URIRef('3'), self.hasPart_ns),
            None)
        self.assertEqual(
            self.graph.getValueFor(URIRef('3'), self.hasPart_ns,
                                   default=URIRef('4')),
            URIRef('4'))
        # test any
        self.assertEqual(
            self.graph.getValueFor(URIRef('1'), self.hasPart_ns, any=False),
            URIRef('10'))
        # not possible to know which entry will be returned
        self.assert_(
            self.graph.getValueFor(URIRef('2'), self.hasPart_ns, any=True)
            in (URIRef('10'), URIRef('23'), URIRef('25')))
        self.assertRaises(ValueError,
                          self.graph.getValueFor,
                          URIRef('2'),
                          self.hasPart_ns,
                          any=False)

        # test without subject
        self.assertEqual(
            self.graph.getValueFor(None, self.hasPart_ns, URIRef('23')),
            URIRef('2'))
        self.assertEqual(
            self.graph.getValueFor(None, self.hasPart_ns, URIRef('3')),
            None)
        self.assertEqual(
            self.graph.getValueFor(None, self.hasPart_ns, URIRef('3'),
                                   default=URIRef('666')),
            URIRef('666'))
        self.assert_(
            self.graph.getValueFor(None, self.hasPart_ns, URIRef('10'),
                                   any=True)
            in (URIRef('1'), URIRef('2')))
        self.assertRaises(ValueError,
                          self.graph.getValueFor,
                          None,
                          self.hasPart_ns,
                          URIRef('10'),
                          any=False)

        # test without predicate
        self.assertEqual(
            self.graph.getValueFor(URIRef('2'), None, URIRef('23')),
            self.hasPart_ns)
        self.assertEqual(
            self.graph.getValueFor(URIRef('1'), None, URIRef('3')),
            None)
        self.assertEqual(
            self.graph.getValueFor(URIRef('1'), None, URIRef('3'),
                                   default=6),
            6)
        self.graph.addRelationFor(URIRef('1'), self.isPartOf_ns, URIRef('10'))
        self.assert_(
            self.graph.getValueFor(URIRef('1'), None, URIRef('10'),
                                   any=True)
            in (self.hasPart_ns, self.isPartOf_ns))
        self.assertRaises(ValueError,
                          self.graph.getValueFor,
                          URIRef('1'),
                          None,
                          URIRef('10'),
                          any=False)

    def test_getRelationsFor(self):
        self.assertEqual(
            self.graph.getRelationsFor(URIRef('1'), self.hasPart_ns),
            (URIRef('10'),))
        self.assertEqual(
            self.graph.getRelationsFor(URIRef('2'), self.hasPart_ns),
            (URIRef('23'), URIRef('25'), URIRef('10')))

    def test_getInverseRelationsFor(self):
        self.assertEqual(
            self.graph.getInverseRelationsFor(URIRef('10'), self.hasPart_ns),
            (URIRef('1'), URIRef('2')))

    def test_removeRelationsFor(self):
        self.assertEqual(
            self.graph.getRelationsFor(URIRef('10'), self.isPartOf_ns),
            (URIRef('1'), URIRef('2')))
        self.graph.addRelationFor(URIRef('10'), self.hasPart_ns, URIRef('666'))
        self.assertEqual(
            self.graph.getRelationsFor(URIRef('10'), self.hasPart_ns),
            (URIRef('666'),))
        self.graph.removeRelationsFor(URIRef('10'), self.isPartOf_ns)
        self.assertEqual(
            self.graph.getRelationsFor(URIRef('10'), self.isPartOf_ns),
            ())
        self.assertEqual(
            self.graph.getRelationsFor(URIRef('10'), self.hasPart_ns),
            (URIRef('666'),))

    def test_removeAllRelationsFor(self):
        self.assertEqual(
            self.graph.getRelationsFor(URIRef('10'), self.isPartOf_ns),
            (URIRef('1'), URIRef('2')))
        self.graph.addRelationFor(URIRef('10'), self.hasPart_ns, URIRef('666'))
        self.assertEqual(
            self.graph.getRelationsFor(URIRef('10'), self.hasPart_ns),
            (URIRef('666'),))
        self.graph.removeAllRelationsFor(URIRef('10'))
        self.assertEqual(
            self.graph.getRelationsFor(URIRef('10'), self.isPartOf_ns),
            ())
        self.assertEqual(
            self.graph.getRelationsFor(URIRef('10'), self.hasPart_ns),
            ())

def test_suite():
    suite = unittest.TestSuite()
    if USE_RDF:
        suite.addTest(unittest.makeSuite(TestRDFGraph))
    return suite

if __name__ == '__main__':
    framework()
