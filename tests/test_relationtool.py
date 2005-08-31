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
"""Tests for Relations Tool
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Interface.Verify import verifyClass

from Products.CPSRelation.tests.CPSRelationTestCase import USE_RDF

if USE_RDF:
    from rdflib import URIRef

from Products.CPSRelation.relationtool import RelationTool
from Products.CPSRelation.interfaces.IRelationTool import IRelationTool
from Products.CPSRelation.tests.CPSRelationTestCase import IOBTreeGraphTestCase
if USE_RDF:
    from Products.CPSRelation.tests.CPSRelationTestCase import RDFGraphTestCase
    from Products.CPSRelation.tests.CPSRelationTestCase import RDF_NAMESPACE
else:
    class RDFGraphTestCase:
        pass

class TestRelationToolIOBTreeGraph(IOBTreeGraphTestCase):
    """Test Relations Tool"""

    def test_interface(self):
        verifyClass(IRelationTool, RelationTool)

    def test_creation(self):
        tool = RelationTool()
        self.assertEqual(tool.getId(), 'portal_relations')
        self.assertEqual(tool.meta_type, 'Relation Tool')

    def test_test_case_tool(self):
        self.assertNotEqual(self.rtool, None)
        self.assertEqual(self.rtool.getId(), 'portal_relations')
        self.assertEqual(self.rtool.meta_type, 'Relation Tool')
        self.assert_(isinstance(self.rtool, RelationTool))

    def test_listGraphIds(self):
        self.assertEqual(self.rtool.listGraphIds(), ['iobtreegraph'])

    def test_deleteAllGraphs(self):
        self.assertEqual(self.rtool.listGraphIds(), ['iobtreegraph'])
        self.rtool.deleteAllGraphs()
        self.assertEqual(self.rtool.listGraphIds(), [])

    def test_hasGraph(self):
        self.assertEqual(self.rtool.hasGraph('iobtreegraph'), True)
        self.assertEqual(self.rtool.hasGraph('iobtreegrapheuh'), False)

    def test_addGraph(self):
        self.assertEqual(self.rtool.listGraphIds(), ['iobtreegraph'])
        self.rtool.addGraph('test_graph', 'IOBTree Graph')
        self.assertEqual(self.rtool.listGraphIds(),
                         ['test_graph', 'iobtreegraph'])
        test_graph = self.rtool.getGraph('test_graph')
        self.assertEqual(test_graph.getId(), 'test_graph')
        self.assertEqual(test_graph.meta_type, 'IOBTree Graph')

    def test_deleteGraph(self):
        self.assertEqual(self.rtool.listGraphIds(), ['iobtreegraph'])
        self.rtool.addGraph('test_graph', 'IOBTree Graph')
        self.assertEqual(self.rtool.listGraphIds(),
                         ['test_graph', 'iobtreegraph'])
        self.rtool.deleteGraph('test_graph')
        self.assertEqual(self.rtool.listGraphIds(), ['iobtreegraph'])

    def test_getGraph(self):
        test_graph = self.rtool.getGraph('iobtreegraph')
        self.assertEqual(test_graph, self.graph)
        self.assertEqual(test_graph.getId(), 'iobtreegraph')
        self.assertEqual(test_graph.meta_type, 'IOBTree Graph')

    def test_serializeGraph(self):
        self.assertRaises(NotImplementedError,
                          self.rtool.serializeGraph,
                          'iobtreegraph')

    def test_listRelationIds(self):
        self.assertEqual(self.rtool.listRelationIds('iobtreegraph'),
                         ['hasPart', 'isPartOf'])

    def test_deleteAllRelations(self):
        self.assertEqual(self.rtool.listRelationIds('iobtreegraph'),
                         ['hasPart', 'isPartOf'])
        self.rtool.deleteAllRelations('iobtreegraph')
        self.assertEqual(self.rtool.listRelationIds('iobtreegraph'), [])

    def test_hasRelation(self):
        self.assertEqual(self.rtool.hasRelation('iobtreegraph', 'hasPart'),
                         True)
        self.assertEqual(self.rtool.hasRelation('iobtreegraph', 'isPartOf'),
                         True)
        self.assertEqual(self.rtool.hasRelation('iobtreegraph', 'dummy'),
                         False)

    def test_addRelation(self):
        self.assertRaises(ValueError,
                          self.rtool.addRelation,
                          'iobtreegraph',
                          'isPartOf',
                          inverse_id='hasPart',
                          title='is part of')
        self.assertEqual(self.rtool.hasRelation('iobtreegraph', 'dummy'), False)
        self.rtool.addRelation('iobtreegraph',
                               'dummy',
                               inverse_id='',
                               title='dummy relation')
        self.assertEqual(self.rtool.hasRelation('iobtreegraph', 'dummy'), True)

    def test_deleteRelation(self):
        self.assertEqual(self.rtool.hasRelation('iobtreegraph', 'hasPart'),
                         True)
        self.rtool.deleteRelation('iobtreegraph', 'hasPart')
        self.assertEqual(self.rtool.hasRelation('iobtreegraph', 'hasPart'),
                         False)

    def test_hasRelationFor(self):
        self.assertEqual(
            self.rtool.hasRelationFor('iobtreegraph', 1, 'hasPart'), True)
        self.assertEqual(
            self.rtool.hasRelationFor('iobtreegraph', 10, 'hasPart'), False)

    def test_addRelationFor(self):
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 10, 'isPartOf'),
            (1, 2))

        self.rtool.addRelationFor('iobtreegraph', 10, 'isPartOf', 3)

        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 10, 'isPartOf'),
            (1, 2, 3))
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 3, 'hasPart'),
            (10,))

    def test_deleteRelationFor(self):
        self.rtool.deleteRelationFor('iobtreegraph', 1, 'hasPart', 10)

        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 1, 'hasPart'),
            ())
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 2, 'hasPart'),
            (10, 23, 25))
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 10, 'isPartOf'),
            (2,))
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 23, 'isPartOf'),
            (2,))
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 25, 'isPartOf'),
            (2,))

    def test_getValueFor(self):
        # 1 --hasPart--> 10
        # 2 --hasPart--> 10, 23, 25
        self.assertEqual(self.rtool.getValueFor('iobtreegraph', 1, 'hasPart'),
                         10)
        # test default
        self.assertEqual(self.rtool.getValueFor('iobtreegraph', 3, 'hasPart'),
                         None)
        self.assertEqual(self.rtool.getValueFor('iobtreegraph', 3, 'hasPart',
                                                default=4),
                         4)
        # test any
        self.assertEqual(
            self.rtool.getValueFor('iobtreegraph', 1, 'hasPart', any=False),
            10)
        # not possible to know which entry will be returned
        self.assert_(
            self.rtool.getValueFor('iobtreegraph', 2, 'hasPart', any=True)
            in (10, 23, 25))
        self.assertRaises(ValueError,
                          self.rtool.getValueFor,
                          'iobtreegraph',
                          2,
                          'hasPart',
                          any=False)

    def test_getRelationsFor(self):
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 1, 'hasPart'),
            (10,))
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 2, 'hasPart'),
            (10, 23, 25))
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 10, 'isPartOf'),
            (1, 2))
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 23, 'isPartOf'),
            (2,))
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 25, 'isPartOf'),
            (2,))

    def test_getInverseRelationsFor(self):
        self.assertEqual(
            self.rtool.getInverseRelationsFor('iobtreegraph', 1, 'isPartOf'),
            (10,))
        self.assertEqual(
            self.rtool.getInverseRelationsFor('iobtreegraph', 2, 'isPartOf'),
            (10, 23, 25,))
        self.assertEqual(
            self.rtool.getInverseRelationsFor('iobtreegraph', 10, 'hasPart'),
            (1, 2))
        self.assertEqual(
            self.rtool.getInverseRelationsFor('iobtreegraph', 23, 'hasPart'),
            (2,))
        self.assertEqual(
            self.rtool.getInverseRelationsFor('iobtreegraph', 25, 'hasPart'),
            (2,))

    def test_removeRelationsFor(self):
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 2, 'hasPart'),
            (10, 23, 25))
        self.rtool.removeRelationsFor('iobtreegraph', 2, 'hasPart')
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 2, 'hasPart'),
            ())

    def test_removeAllRelationsFor(self):
        self.rtool.addRelationFor('iobtreegraph', 2, 'isPartOf', 3)
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 2, 'hasPart'),
            (10, 23, 25))
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 2, 'isPartOf'),
            (3,))
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 10, 'isPartOf'),
            (1, 2))

        self.rtool.removeAllRelationsFor('iobtreegraph', 2)

        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 2, 'hasPart'),
            ())
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 2, 'isPartOf'),
            ())
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 10, 'isPartOf'),
            (1,))


class TestRelationToolRDFGraph(RDFGraphTestCase):
    """Test Relations Tool"""

    def test_interface(self):
        verifyClass(IRelationTool, RelationTool)

    def test_creation(self):
        tool = RelationTool()
        self.assertEqual(tool.getId(), 'portal_relations')
        self.assertEqual(tool.meta_type, 'Relation Tool')

    def test_test_case_tool(self):
        self.assertNotEqual(self.rtool, None)
        self.assertEqual(self.rtool.getId(), 'portal_relations')
        self.assertEqual(self.rtool.meta_type, 'Relation Tool')
        self.assert_(isinstance(self.rtool, RelationTool))

    def test_listGraphIds(self):
        self.assertEqual(self.rtool.listGraphIds(), ['rdfgraph'])

    def test_deleteAllGraphs(self):
        self.assertEqual(self.rtool.listGraphIds(), ['rdfgraph'])
        self.rtool.deleteAllGraphs()
        self.assertEqual(self.rtool.listGraphIds(), [])

    def test_hasGraph(self):
        self.assertEqual(self.rtool.hasGraph('rdfgraph'), True)
        self.assertEqual(self.rtool.hasGraph('rdfgrapheuh'), False)

    def test_addGraph(self):
        self.assertEqual(self.rtool.listGraphIds(), ['rdfgraph'])
        self.rtool.addGraph('test_graph', 'RDF Graph')
        self.assertEqual(self.rtool.listGraphIds(),
                         ['test_graph', 'rdfgraph'])
        test_graph = self.rtool.getGraph('test_graph')
        self.assertEqual(test_graph.getId(), 'test_graph')
        self.assertEqual(test_graph.meta_type, 'RDF Graph')

    def test_deleteGraph(self):
        self.assertEqual(self.rtool.listGraphIds(), ['rdfgraph'])
        self.rtool.addGraph('test_graph', 'RDF Graph')
        self.assertEqual(self.rtool.listGraphIds(),
                         ['test_graph', 'rdfgraph'])
        self.rtool.deleteGraph('test_graph')
        self.assertEqual(self.rtool.listGraphIds(), ['rdfgraph'])

    def test_getGraph(self):
        test_graph = self.rtool.getGraph('rdfgraph')
        self.assertEqual(test_graph, self.graph)
        self.assertEqual(test_graph.getId(), 'rdfgraph')
        self.assertEqual(test_graph.meta_type, 'RDF Graph')

    def test_serializeGraph(self):
        serialized = self.rtool.serializeGraph('rdfgraph')
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
        self.assertEqual(self.rtool.listRelationIds('rdfgraph'),
                         [self.hasPart_ns, self.isPartOf_ns])

    def test_deleteAllRelations(self):
        self.assertEqual(self.rtool.listRelationIds('rdfgraph'),
                         [self.hasPart_ns, self.isPartOf_ns])
        self.rtool.deleteAllRelations('rdfgraph')
        self.assertEqual(self.rtool.listRelationIds('rdfgraph'), [])

    def test_hasRelation(self):
        self.assertEqual(self.rtool.hasRelation('rdfgraph', self.hasPart_ns),
                         True)
        self.assertEqual(self.rtool.hasRelation('rdfgraph', self.isPartOf_ns),
                         True)
        self.assertEqual(
            self.rtool.hasRelation('rdfgraph', RDF_NAMESPACE['dummy']),
            False)

    def test_addRelation(self):
        # XXX Nothing done when adding a relation
        new_relation = RDF_NAMESPACE['dummy']
        self.assertEqual(
            self.rtool.hasRelation('rdfgraph', new_relation),
            False)
        self.rtool.addRelation('rdfgraph',
                               new_relation,
                               inverse_id='',
                               title='dummy relation')
        self.assertEqual(
            self.rtool.hasRelation('rdfgraph', new_relation),
            False)
        # Add a relation instance
        self.rtool.addRelationFor('rdfgraph', URIRef('10'),
                                  new_relation, URIRef('3'))
        self.assertEqual(
            self.rtool.hasRelation('rdfgraph', new_relation),
            True)

    def test_deleteRelation(self):
        self.assertEqual(self.rtool.hasRelation('rdfgraph', self.hasPart_ns),
                         True)
        self.rtool.deleteRelation('rdfgraph', self.hasPart_ns)
        self.assertEqual(self.rtool.hasRelation('rdfgraph', self.hasPart_ns),
                         False)

    def test_hasRelationFor(self):
        self.assertEqual(
            self.rtool.hasRelationFor('rdfgraph',
                                      URIRef('1'), self.hasPart_ns),
            True)
        self.assertEqual(
            self.rtool.hasRelationFor('rdfgraph',
                                      URIRef('10'), self.hasPart_ns),
            False)

    def test_addRelationFor(self):
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('10'), self.isPartOf_ns),
            (URIRef('1'), URIRef('2')))

        self.rtool.addRelationFor('rdfgraph',
                                  URIRef('10'), self.isPartOf_ns, URIRef('3'))

        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('10'), self.isPartOf_ns),
            (URIRef('1'), URIRef('2'), URIRef('3')))
        # XXX inverse relation is not added
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('3'), self.hasPart_ns),
            ())

    def test_deleteRelationFor(self):
        self.rtool.deleteRelationFor('rdfgraph',
                                     URIRef('1'), self.hasPart_ns, URIRef('10'))

        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('1'), self.hasPart_ns),
            ())
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.hasPart_ns),
            (URIRef('10'), URIRef('23'), URIRef('25')))
        # XXX inverse relation is not deleted
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('10'), self.isPartOf_ns),
            (URIRef('1'), URIRef('2'),))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('23'), self.isPartOf_ns),
            (URIRef('2'),))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('25'), self.isPartOf_ns),
            (URIRef('2'),))

    def test_getValueFor(self):
        # 1 --hasPart--> 10
        # 2 --hasPart--> 10, 23, 25
        self.assertEqual(
            self.rtool.getValueFor('rdfgraph', URIRef('1'), self.hasPart_ns),
            URIRef('10'))
        # test default
        self.assertEqual(
            self.rtool.getValueFor('rdfgraph', URIRef('3'), self.hasPart_ns),
            None)
        self.assertEqual(
            self.rtool.getValueFor('rdfgraph', URIRef('3'), self.hasPart_ns,
                                   default=URIRef('4')),
            URIRef('4'))
        # test any
        self.assertEqual(
            self.rtool.getValueFor('rdfgraph', URIRef('1'), self.hasPart_ns, any=False),
            URIRef('10'))
        # not possible to know which entry will be returned
        self.assert_(
            self.rtool.getValueFor('rdfgraph', URIRef('2'), self.hasPart_ns, any=True)
            in (URIRef('10'), URIRef('23'), URIRef('25')))
        self.assertRaises(ValueError,
                          self.rtool.getValueFor,
                          'rdfgraph',
                          URIRef('2'),
                          self.hasPart_ns,
                          any=False)

    def test_getRelationsFor(self):
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('1'), self.hasPart_ns),
            (URIRef('10'),))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.hasPart_ns),
            (URIRef('10'), URIRef('23'), URIRef('25')))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('10'), self.isPartOf_ns),
            (URIRef('1'), URIRef('2')))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('23'), self.isPartOf_ns),
            (URIRef('2'),))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('25'), self.isPartOf_ns),
            (URIRef('2'),))

    def test_getInverseRelationsFor(self):
        self.assertEqual(
            self.rtool.getInverseRelationsFor('rdfgraph',
                                              URIRef('1'), self.isPartOf_ns),
            (URIRef('10'),))
        self.assertEqual(
            self.rtool.getInverseRelationsFor('rdfgraph',
                                              URIRef('2'), self.isPartOf_ns),
            (URIRef('10'), URIRef('23'), URIRef('25'),))
        self.assertEqual(
            self.rtool.getInverseRelationsFor('rdfgraph',
                                              URIRef('10'), self.hasPart_ns),
            (URIRef('1'), URIRef('2')))
        self.assertEqual(
            self.rtool.getInverseRelationsFor('rdfgraph',
                                              URIRef('23'), self.hasPart_ns),
            (URIRef('2'),))
        self.assertEqual(
            self.rtool.getInverseRelationsFor('rdfgraph',
                                              URIRef('25'), self.hasPart_ns),
            (URIRef('2'),))

    def test_removeRelationsFor(self):
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.hasPart_ns),
            (URIRef('10'), URIRef('23'), URIRef('25')))
        self.rtool.removeRelationsFor('rdfgraph',
                                      URIRef('2'), self.hasPart_ns)
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.hasPart_ns),
            ())

    def test_removeAllRelationsFor(self):
        self.rtool.addRelationFor('rdfgraph',
                                  URIRef('2'), self.isPartOf_ns, URIRef('3'))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.hasPart_ns),
            (URIRef('10'), URIRef('23'), URIRef('25')))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.isPartOf_ns),
            (URIRef('3'),))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('10'), self.isPartOf_ns),
            (URIRef('1'), URIRef('2')))

        self.rtool.removeAllRelationsFor('rdfgraph', URIRef('2'))

        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.hasPart_ns),
            ())
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.isPartOf_ns),
            ())
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('10'), self.isPartOf_ns),
            (URIRef('1'),))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRelationToolIOBTreeGraph))
    if USE_RDF:
        suite.addTest(unittest.makeSuite(TestRelationToolRDFGraph))
    return suite

if __name__ == '__main__':
    framework()
