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
#-------------------------------------------------------------------------------
"""Tests for Relations Tool
"""

import os
import unittest

from zope.interface.verify import verifyClass

from Products.CPSRelation.tests.CPSRelationTestCase import USE_RDFLIB
from Products.CPSRelation.tests.CPSRelationTestCase import USE_REDLAND

if USE_RDFLIB:
    from Products.CPSRelation.rdflibgraph import URIRef
if USE_REDLAND:
    from Products.CPSRelation.redlandgraph import Node, Uri

from Products.CPSRelation.relationtool import RelationTool
from Products.CPSRelation.interfaces import IRelationTool
from Products.CPSRelation.tests.CPSRelationTestCase import IOBTreeGraphTestCase
from Products.CPSRelation.tests.test_graphregistry import DEFAULT_GRAPH_TYPES

if USE_RDFLIB:
    from Products.CPSRelation.tests.CPSRelationTestCase import RdflibGraphTestCase
    from Products.CPSRelation.tests.CPSRelationTestCase import RDFLIB_NAMESPACE
else:
    class RdflibGraphTestCase:
        pass

if USE_REDLAND:
    from Products.CPSRelation.tests.CPSRelationTestCase import RedlandGraphTestCase
    from Products.CPSRelation.tests.CPSRelationTestCase import REDLAND_NAMESPACE
else:
    class RedlandGraphTestCase:
        pass

class TestRelationToolIOBTreeGraph(IOBTreeGraphTestCase):
    """Test Relations Tool with and iobtree graph
    """

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

    def test_getSupportedGraphTypes(self):
        self.assertEquals(self.rtool.getSupportedGraphTypes(),
                          DEFAULT_GRAPH_TYPES)

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

    def test_parseGraph(self):
        self.assertRaises(NotImplementedError,
                          self.rtool.parseGraph,
                          'iobtreegraph',
                          'source')

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

    def test_addRelationsFor(self):
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 10, 'isPartOf'),
            (1, 2))
        new_rel = (
            (10, 'isPartOf', 3),
            (10, 'isPartOf', 23),
            )
        self.rtool.addRelationsFor('iobtreegraph', new_rel)
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 10, 'isPartOf'),
            (1, 2, 3, 23))
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 3, 'hasPart'),
            (10,))
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 23, 'hasPart'),
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

    def test_deleteRelationsFor(self):
        del_rel = (
            (1, 'hasPart', 10),
            (2, 'hasPart', 23),
            )
        self.rtool.deleteRelationsFor('iobtreegraph', del_rel)

        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 1, 'hasPart'),
            ())
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 2, 'hasPart'),
            (10, 25))
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 10, 'isPartOf'),
            (2,))
        self.assertEqual(
            self.rtool.getRelationsFor('iobtreegraph', 23, 'isPartOf'),
            ())
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

    def test_getAllRelationsFor(self):
        self.assertEqual(
            self.rtool.getAllRelationsFor('iobtreegraph', 1),
            [('hasPart', 10)])
        self.assertEqual(
            self.rtool.getAllRelationsFor('iobtreegraph', 2),
            [('hasPart', 10),
             ('hasPart', 23),
             ('hasPart', 25),
             ])
        self.assertEqual(
            self.rtool.getAllRelationsFor('iobtreegraph', 10),
            [('isPartOf', 1),
             ('isPartOf', 2),
             ])
        self.assertEqual(
            self.rtool.getAllRelationsFor('iobtreegraph', 23),
            [('isPartOf', 2)])
        self.assertEqual(
            self.rtool.getAllRelationsFor('iobtreegraph', 25),
            [('isPartOf', 2)])

    def test_getAllInverseRelationsFor(self):
        self.assertEqual(
            self.rtool.getAllInverseRelationsFor('iobtreegraph', 1),
            [(10, 'isPartOf')])
        self.assertEqual(
            self.rtool.getAllInverseRelationsFor('iobtreegraph', 2),
            [(10, 'isPartOf'),
             (23, 'isPartOf'),
             (25, 'isPartOf'),
             ])
        self.assertEqual(
            self.rtool.getAllInverseRelationsFor('iobtreegraph', 10),
            [(1, 'hasPart'),
             (2, 'hasPart'),
             ])
        self.assertEqual(
            self.rtool.getAllInverseRelationsFor('iobtreegraph', 23),
            [(2, 'hasPart')])
        self.assertEqual(
            self.rtool.getAllInverseRelationsFor('iobtreegraph', 25),
            [(2, 'hasPart')])

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

    def test_queryGraph(self):
        self.assertRaises(NotImplementedError,
                          self.rtool.queryGraph,
                          'iobtreegraph',
                          'query :)')


class TestRelationToolRdflibGraph(RdflibGraphTestCase):
    """Test Relations Tool with a rdflib graph
    """

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
        self.rtool.addGraph('test_graph', 'Rdflib Graph')
        self.assertEqual(self.rtool.listGraphIds(),
                         ['test_graph', 'rdfgraph'])
        test_graph = self.rtool.getGraph('test_graph')
        self.assertEqual(test_graph.getId(), 'test_graph')
        self.assertEqual(test_graph.meta_type, 'Rdflib Graph')

    def test_deleteGraph(self):
        self.assertEqual(self.rtool.listGraphIds(), ['rdfgraph'])
        self.rtool.addGraph('test_graph', 'Rdflib Graph')
        self.assertEqual(self.rtool.listGraphIds(),
                         ['test_graph', 'rdfgraph'])
        self.rtool.deleteGraph('test_graph')
        self.assertEqual(self.rtool.listGraphIds(), ['rdfgraph'])

    def test_getGraph(self):
        test_graph = self.rtool.getGraph('rdfgraph')
        self.assertEqual(test_graph, self.graph)
        self.assertEqual(test_graph.getId(), 'rdfgraph')
        self.assertEqual(test_graph.meta_type, 'Rdflib Graph')

    def test_parseGraph_file(self):
        self.rtool.addGraph('test_graph', 'Rdflib Graph')
        from Products.CPSRelation import tests as here_tests
        input_source = os.path.join(here_tests.__path__[0],
                                    'test_files/rdf_graph.xml')
        self.rtool.parseGraph('test_graph', input_source,
                              publicID='Dummy publicID')
        all_relations = [
            (URIRef('1'), self.hasPart, URIRef('10')),
            (URIRef('2'), self.hasPart, URIRef('10')),
            (URIRef('2'), self.hasPart, URIRef('23')),
            (URIRef('2'), self.hasPart, URIRef('25')),
            (URIRef('10'), self.isPartOf, URIRef('1')),
            (URIRef('10'), self.isPartOf, URIRef('2')),
            (URIRef('23'), self.isPartOf, URIRef('2')),
            (URIRef('25'), self.isPartOf, URIRef('2')),
            ]
        test_graph = self.rtool.getGraph('test_graph')
        self.assertEqual(test_graph.listAllRelations(), all_relations)

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
                         [self.hasPart, self.isPartOf])

    def test_deleteAllRelations(self):
        self.assertEqual(self.rtool.listRelationIds('rdfgraph'),
                         [self.hasPart, self.isPartOf])
        self.rtool.deleteAllRelations('rdfgraph')
        self.assertEqual(self.rtool.listRelationIds('rdfgraph'), [])

    def test_hasRelation(self):
        self.assertEqual(self.rtool.hasRelation('rdfgraph', self.hasPart),
                         True)
        self.assertEqual(self.rtool.hasRelation('rdfgraph', self.isPartOf),
                         True)
        self.assertEqual(
            self.rtool.hasRelation('rdfgraph', RDFLIB_NAMESPACE['dummy']),
            False)

    def test_addRelation(self):
        # XXX Nothing done when adding a relation
        new_relation = RDFLIB_NAMESPACE['dummy']
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
        self.assertEqual(self.rtool.hasRelation('rdfgraph', self.hasPart),
                         True)
        self.rtool.deleteRelation('rdfgraph', self.hasPart)
        self.assertEqual(self.rtool.hasRelation('rdfgraph', self.hasPart),
                         False)

    def test_hasRelationFor(self):
        self.assertEqual(
            self.rtool.hasRelationFor('rdfgraph',
                                      URIRef('1'), self.hasPart),
            True)
        self.assertEqual(
            self.rtool.hasRelationFor('rdfgraph',
                                      URIRef('10'), self.hasPart),
            False)

    def test_addRelationFor(self):
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('10'), self.isPartOf),
            (URIRef('1'), URIRef('2')))

        self.rtool.addRelationFor('rdfgraph',
                                  URIRef('10'), self.isPartOf, URIRef('3'))

        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('10'), self.isPartOf),
            (URIRef('1'), URIRef('2'), URIRef('3')))
        # XXX inverse relation is not added
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('3'), self.hasPart),
            ())

    def test_addRelationsFor(self):
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('10'), self.isPartOf),
            (URIRef('1'), URIRef('2')))
        new_rel = (
            (URIRef('10'), self.isPartOf, URIRef('3')),
            (URIRef('10'), self.isPartOf, URIRef('23')),
            )
        self.rtool.addRelationsFor('rdfgraph', new_rel)
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('10'), self.isPartOf),
            (URIRef('1'), URIRef('2'), URIRef('3'), URIRef('23')))
        # XXX inverse relations are not added
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('3'), self.hasPart),
            ())
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('23'), self.hasPart),
            ())

    def test_deleteRelationFor(self):
        self.rtool.deleteRelationFor('rdfgraph',
                                     URIRef('1'), self.hasPart, URIRef('10'))

        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('1'), self.hasPart),
            ())
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.hasPart),
            (URIRef('10'), URIRef('23'), URIRef('25')))
        # XXX inverse relation is not deleted
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('10'), self.isPartOf),
            (URIRef('1'), URIRef('2'),))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('23'), self.isPartOf),
            (URIRef('2'),))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('25'), self.isPartOf),
            (URIRef('2'),))

    def test_deleteRelationsFor(self):
        del_rel = (
            (URIRef('1'), self.hasPart, URIRef('10')),
            (URIRef('2'), self.hasPart, URIRef('23')),
            )
        self.rtool.deleteRelationsFor('rdfgraph', del_rel)

        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('1'), self.hasPart),
            ())
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.hasPart),
            (URIRef('10'), URIRef('25')))
        # XXX inverse relation is not deleted
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('10'), self.isPartOf),
            (URIRef('1'), URIRef('2'),))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('23'), self.isPartOf),
            (URIRef('2'),))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('25'), self.isPartOf),
            (URIRef('2'),))

    def test_getValueFor(self):
        # 1 --hasPart--> 10
        # 2 --hasPart--> 10, 23, 25
        self.assertEqual(
            self.rtool.getValueFor('rdfgraph', URIRef('1'), self.hasPart),
            URIRef('10'))
        # test default
        self.assertEqual(
            self.rtool.getValueFor('rdfgraph', URIRef('3'), self.hasPart),
            None)
        self.assertEqual(
            self.rtool.getValueFor('rdfgraph', URIRef('3'), self.hasPart,
                                   default=URIRef('4')),
            URIRef('4'))
        # test any
        self.assertEqual(
            self.rtool.getValueFor('rdfgraph', URIRef('1'), self.hasPart, any=False),
            URIRef('10'))
        # not possible to know which entry will be returned
        self.assert_(
            self.rtool.getValueFor('rdfgraph', URIRef('2'), self.hasPart, any=True)
            in (URIRef('10'), URIRef('23'), URIRef('25')))
        self.assertRaises(ValueError,
                          self.rtool.getValueFor,
                          'rdfgraph',
                          URIRef('2'),
                          self.hasPart,
                          any=False)

    def test_getRelationsFor(self):
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('1'), self.hasPart),
            (URIRef('10'),))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.hasPart),
            (URIRef('10'), URIRef('23'), URIRef('25')))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('10'), self.isPartOf),
            (URIRef('1'), URIRef('2')))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('23'), self.isPartOf),
            (URIRef('2'),))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('25'), self.isPartOf),
            (URIRef('2'),))

    def test_getInverseRelationsFor(self):
        self.assertEqual(
            self.rtool.getInverseRelationsFor('rdfgraph',
                                              URIRef('1'), self.isPartOf),
            (URIRef('10'),))
        self.assertEqual(
            self.rtool.getInverseRelationsFor('rdfgraph',
                                              URIRef('2'), self.isPartOf),
            (URIRef('10'), URIRef('23'), URIRef('25'),))
        self.assertEqual(
            self.rtool.getInverseRelationsFor('rdfgraph',
                                              URIRef('10'), self.hasPart),
            (URIRef('1'), URIRef('2')))
        self.assertEqual(
            self.rtool.getInverseRelationsFor('rdfgraph',
                                              URIRef('23'), self.hasPart),
            (URIRef('2'),))
        self.assertEqual(
            self.rtool.getInverseRelationsFor('rdfgraph',
                                              URIRef('25'), self.hasPart),
            (URIRef('2'),))


    def test_getAllRelationsFor(self):
        self.assertEqual(
            self.rtool.getAllRelationsFor('rdfgraph', URIRef('1')),
            [(self.hasPart, URIRef('10'))])
        self.assertEqual(
            self.rtool.getAllRelationsFor('rdfgraph', URIRef('2')),
            [(self.hasPart, URIRef('10')),
             (self.hasPart, URIRef('23')),
             (self.hasPart, URIRef('25')),
             ])
        self.assertEqual(
            self.rtool.getAllRelationsFor('rdfgraph', URIRef('10')),
            [(self.isPartOf, URIRef('1')),
             (self.isPartOf, URIRef('2')),
             ])
        self.assertEqual(
            self.rtool.getAllRelationsFor('rdfgraph', URIRef('23')),
            [(self.isPartOf, URIRef('2'))])
        self.assertEqual(
            self.rtool.getAllRelationsFor('rdfgraph', URIRef('25')),
            [(self.isPartOf, URIRef('2'))])

    def test_getAllInverseRelationsFor(self):
        self.assertEqual(
            self.rtool.getAllInverseRelationsFor('rdfgraph', URIRef('1')),
            [(URIRef('10'), self.isPartOf)])
        self.assertEqual(
            self.rtool.getAllInverseRelationsFor('rdfgraph', URIRef('2')),
            [(URIRef('10'), self.isPartOf),
             (URIRef('23'), self.isPartOf),
             (URIRef('25'), self.isPartOf),
             ])
        self.assertEqual(
            self.rtool.getAllInverseRelationsFor('rdfgraph', URIRef('10')),
            [(URIRef('1'), self.hasPart),
             (URIRef('2'), self.hasPart),
             ])
        self.assertEqual(
            self.rtool.getAllInverseRelationsFor('rdfgraph', URIRef('23')),
            [(URIRef('2'), self.hasPart)])
        self.assertEqual(
            self.rtool.getAllInverseRelationsFor('rdfgraph', URIRef('25')),
            [(URIRef('2'), self.hasPart)])

    def test_removeRelationsFor(self):
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.hasPart),
            (URIRef('10'), URIRef('23'), URIRef('25')))
        self.rtool.removeRelationsFor('rdfgraph',
                                      URIRef('2'), self.hasPart)
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.hasPart),
            ())

    def test_removeAllRelationsFor(self):
        self.rtool.addRelationFor('rdfgraph',
                                  URIRef('2'), self.isPartOf, URIRef('3'))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.hasPart),
            (URIRef('10'), URIRef('23'), URIRef('25')))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.isPartOf),
            (URIRef('3'),))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('10'), self.isPartOf),
            (URIRef('1'), URIRef('2')))

        self.rtool.removeAllRelationsFor('rdfgraph', URIRef('2'))

        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.hasPart),
            ())
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('2'), self.isPartOf),
            ())
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       URIRef('10'), self.isPartOf),
            (URIRef('1'),))

    def test_queryGraph(self):
        self.assertRaises(NotImplementedError,
                          self.rtool.queryGraph,
                          'rdfgraph',
                          'query :)')


class TestRelationToolRedlandGraph(RedlandGraphTestCase):
    """Test Relations Tool with a redland graph
    """

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
        self.rtool.addGraph('test_graph', 'Redland Graph', backend='memory')
        self.assertEqual(self.rtool.listGraphIds(),
                         ['test_graph', 'rdfgraph'])
        test_graph = self.rtool.getGraph('test_graph')
        self.assertEqual(test_graph.getId(), 'test_graph')
        self.assertEqual(test_graph.meta_type, 'Redland Graph')

    def test_deleteGraph(self):
        self.assertEqual(self.rtool.listGraphIds(), ['rdfgraph'])
        self.rtool.addGraph('test_graph', 'Redland Graph', backend='memory')
        self.assertEqual(self.rtool.listGraphIds(),
                         ['test_graph', 'rdfgraph'])
        self.rtool.deleteGraph('test_graph')
        self.assertEqual(self.rtool.listGraphIds(), ['rdfgraph'])

    def test_getGraph(self):
        test_graph = self.rtool.getGraph('rdfgraph')
        self.assertEqual(test_graph, self.graph)
        self.assertEqual(test_graph.getId(), 'rdfgraph')
        self.assertEqual(test_graph.meta_type, 'Redland Graph')

    def test_parseGraph_file(self):
        self.rtool.addGraph('test_graph', 'Redland Graph', backend='memory')
        from Products.CPSRelation import tests as here_tests
        input_source = os.path.join(here_tests.__path__[0],
                                    'test_files/rdf_graph.xml')
        self.rtool.parseGraph('test_graph', 'file:'+input_source,
                              publicID=Uri('y'))
        all_relations = [
            ('[y1]', str(self.hasPart), '[y10]'),
            ('[y2]', str(self.hasPart), '[y10]'),
            ('[y2]', str(self.hasPart), '[y23]'),
            ('[y2]', str(self.hasPart), '[y25]'),
            ('[y10]', str(self.isPartOf), '[y1]'),
            ('[y10]', str(self.isPartOf), '[y2]'),
            ('[y23]', str(self.isPartOf), '[y2]'),
            ('[y25]', str(self.isPartOf), '[y2]'),
            ]
        test_graph = self.rtool.getGraph('test_graph')
        self.assertEqual(test_graph.printAllRelations(), all_relations)

    def test_parseGraph_string(self):
        self.rtool.addGraph('test_graph', 'Redland Graph', backend='memory')
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
        self.rtool.parseGraph('test_graph', input_source,
                              publicID=Uri('x'))
        all_relations = [
            ('[x1]', str(self.hasPart), '[x10]'),
            ('[x2]', str(self.hasPart), '[x10]'),
            ('[x2]', str(self.hasPart), '[x23]'),
            ('[x2]', str(self.hasPart), '[x25]'),
            ('[x10]', str(self.isPartOf), '[x1]'),
            ('[x10]', str(self.isPartOf), '[x2]'),
            ('[x23]', str(self.isPartOf), '[x2]'),
            ('[x25]', str(self.isPartOf), '[x2]'),
            ]
        test_graph = self.rtool.getGraph('test_graph')
        self.assertEqual(test_graph.printAllRelations(), all_relations)

    def test_serializeGraph(self):
        serialized = self.rtool.serializeGraph('rdfgraph')
        # not possible to test xml rendering, it changes every time...
        start = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:cps="http://cps-project.org/2005/data/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">"""
        self.assert_(serialized.startswith(start))
        end = "</rdf:RDF>\n"
        self.assert_(serialized.endswith(end))

    def test_listRelationIds(self):
        self.assertEqual(self.rtool.listRelationIds('rdfgraph'),
                         [str(self.hasPart), str(self.isPartOf)])

    def test_deleteAllRelations(self):
        self.assertEqual(self.rtool.listRelationIds('rdfgraph'),
                         [str(self.hasPart), str(self.isPartOf)])
        self.rtool.deleteAllRelations('rdfgraph')
        self.assertEqual(self.rtool.listRelationIds('rdfgraph'), [])

    def test_hasRelation(self):
        self.assertEqual(self.rtool.hasRelation('rdfgraph', self.hasPart),
                         True)
        self.assertEqual(self.rtool.hasRelation('rdfgraph', self.isPartOf),
                         True)
        self.assertEqual(
            self.rtool.hasRelation('rdfgraph', REDLAND_NAMESPACE['dummy']),
            False)

    def test_addRelation(self):
        self.assertEqual(self.rtool.listRelationIds('rdfgraph'),
                         [str(self.isPartOf), str(self.hasPart)])
        new_relation = REDLAND_NAMESPACE['dummy']
        self.rtool.addRelation('rdfgraph', new_relation)
        self.assertEqual(self.rtool.listRelationIds('rdfgraph'),
                         [str(self.isPartOf), str(self.hasPart)])
        # XXX AT: in RDF graph, relation is added only if a relation instance
        # is added...
        self.rtool.addRelationFor('rdfgraph',
                                  Node(Uri('25')), new_relation, Node(Uri('2')))
        self.assertEqual(self.rtool.listRelationIds('rdfgraph'),
                         [str(self.isPartOf), str(self.hasPart),
                          str(new_relation)])

    def test_deleteRelation(self):
        self.assertEqual(self.rtool.hasRelation('rdfgraph', self.hasPart),
                         True)
        self.rtool.deleteRelation('rdfgraph', self.hasPart)
        self.assertEqual(self.rtool.hasRelation('rdfgraph', self.hasPart),
                         False)

    def test_hasRelationFor(self):
        self.assertEqual(
            self.rtool.hasRelationFor('rdfgraph',
                                      Node(Uri('1')), self.hasPart),
            True)
        self.assertEqual(
            self.rtool.hasRelationFor('rdfgraph',
                                      Node(Uri('10')), self.hasPart),
            False)

    def test_addRelationFor(self):
        self.assertEqual(
            self.rtool.hasRelationFor('rdfgraph', Node(Uri('3')), self.hasPart),
            False)
        self.rtool.addRelationFor('rdfgraph',
                                  Node(Uri('3')), self.hasPart, Node(Uri('10')))
        self.assertEqual(
            self.rtool.hasRelationFor('rdfgraph', Node(Uri('3')), self.hasPart),
            True)

    def test_addRelationsFor(self):
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('10')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[1]', '[2]'))
        new_rel = (
            (Node(Uri('10')), self.isPartOf, Node(Uri('3'))),
            (Node(Uri('10')), self.isPartOf, Node(Uri('23'))),
            )
        self.rtool.addRelationsFor('rdfgraph', new_rel)
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('10')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[1]', '[2]', '[3]', '[23]'))
        # XXX inverse relations are not added
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       Node(Uri('3')), self.hasPart),
            ())
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       Node(Uri('23')), self.hasPart),
            ())

    def test_deleteRelationFor(self):
        self.rtool.deleteRelationFor('rdfgraph',
                                     Node(Uri('1')), self.hasPart, Node(Uri('10')))
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       Node(Uri('1')), self.hasPart),
            ())
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('2')), self.hasPart)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[10]', '[23]', '[25]'))
        # XXX inverse relation is not deleted
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('10')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[1]', '[2]'))
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('23')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[2]',))
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('25')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[2]',))

    def test_deleteRelationsFor(self):
        del_rel = (
            (Node(Uri('1')), self.hasPart, Node(Uri('10'))),
            (Node(Uri('2')), self.hasPart, Node(Uri('23'))),
            )
        self.rtool.deleteRelationsFor('rdfgraph', del_rel)

        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       Node(Uri('1')), self.hasPart),
            ())
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('2')), self.hasPart)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[10]', '[25]'))
        # XXX inverse relation is not deleted
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('10')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[1]', '[2]'))
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('23')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[2]',))
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('25')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[2]',))

    def test_getValueFor(self):
        # 1 --hasPart--> 10
        # 2 --hasPart--> 10, 23, 25
        self.assertEqual(
            self.rtool.getValueFor('rdfgraph', Node(Uri('1')), self.hasPart),
            Node(Uri('10')))
        # test default
        self.assertEqual(
            self.rtool.getValueFor('rdfgraph', Node(Uri('3')), self.hasPart),
            None)
        self.assertEqual(
            self.rtool.getValueFor('rdfgraph', Node(Uri('3')), self.hasPart,
                                   default=Node(Uri('4'))),
            Node(Uri('4')))
        # test any
        self.assertEqual(
            self.rtool.getValueFor('rdfgraph', Node(Uri('1')), self.hasPart, any=False),
            Node(Uri('10')))
        # not possible to know which entry will be returned
        self.assert_(
            self.rtool.getValueFor('rdfgraph', Node(Uri('2')), self.hasPart, any=True)
            in (Node(Uri('10')), Node(Uri('23')), Node(Uri('25'))))
        self.assertRaises(ValueError,
                          self.rtool.getValueFor,
                          'rdfgraph',
                          Node(Uri('2')),
                          self.hasPart,
                          any=False)

    def test_getRelationsFor(self):
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('1')), self.hasPart)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[10]',))
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('2')), self.hasPart)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[10]', '[23]', '[25]'))
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('10')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[1]', '[2]'))
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('23')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[2]',))
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('25')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[2]',))

    def test_getInverseRelationsFor(self):
        rel = self.rtool.getInverseRelationsFor('rdfgraph',
                                                Node(Uri('1')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[10]',))
        rel = self.rtool.getInverseRelationsFor('rdfgraph',
                                                Node(Uri('2')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[10]', '[23]', '[25]'))
        rel = self.rtool.getInverseRelationsFor('rdfgraph',
                                                Node(Uri('10')), self.hasPart)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[1]', '[2]'))
        rel = self.rtool.getInverseRelationsFor('rdfgraph',
                                                Node(Uri('23')), self.hasPart)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[2]',))
        rel = self.rtool.getInverseRelationsFor('rdfgraph',
                                                Node(Uri('25')), self.hasPart)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[2]',))

    def test_removeRelationsFor(self):
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('2')), self.hasPart)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[10]', '[23]', '[25]'))
        self.rtool.removeRelationsFor('rdfgraph',
                                      Node(Uri('2')), self.hasPart)
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       Node(Uri('2')), self.hasPart),
            ())

    def test_removeAllRelationsFor(self):
        self.rtool.addRelationFor('rdfgraph',
                                  Node(Uri('2')), self.isPartOf, Node(Uri('3')))
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('2')), self.hasPart)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[10]', '[23]', '[25]'))
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('2')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[3]',))
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('10')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[1]', '[2]'))

        self.rtool.removeAllRelationsFor('rdfgraph', Node(Uri('2')))

        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       Node(Uri('2')), self.hasPart),
            ())
        self.assertEqual(
            self.rtool.getRelationsFor('rdfgraph',
                                       Node(Uri('2')), self.isPartOf),
            ())
        rel = self.rtool.getRelationsFor('rdfgraph',
                                         Node(Uri('10')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[1]',))

    def test_queryGraph(self):
        # add other relations for tests
        self.graph.addRelationFor(Node(Uri(('1'))), self.hasPart, Node(Uri('totoro')))
        self.graph.addRelationFor(Node(Uri(('2'))), self.hasPart, Node(Uri(('toto'))))
        self.graph.addRelationFor(Node(Uri(('10'))), self.hasPart, Node(Uri(('tota'))))
        self.graph.addRelationFor(Node(Uri(('toto'))), self.hasPart, Node(Uri(('totoro'))))

        query = """
PREFIX cps: <http://cps-project.org/2005/data/>
SELECT ?subj, ?obj
WHERE {
  ?subj cps:hasPart ?obj .
  FILTER REGEX(?obj, "^[0-9]+")
}
"""
        results = self.rtool.queryGraph('rdfgraph', query, query_language='sparql')
        results = [(str(x['subj']), str(x['obj'])) for x in results]
        expected = [
            ('[1]', '[10]'),
            ('[2]', '[10]'),
            ('[2]', '[23]'),
            ('[2]', '[25]'),
            ]
        self.assertEqual(results, expected)

        # change filter
        query = """
PREFIX cps: <http://cps-project.org/2005/data/>
SELECT ?subj, ?obj
WHERE {
  ?subj cps:hasPart ?obj .
  FILTER REGEX(?obj, "^toto.*")
}
"""
        results = self.rtool.queryGraph('rdfgraph', query, query_language='sparql')
        results = [(str(x['subj']), str(x['obj'])) for x in results]
        expected = [
            ('[1]', '[totoro]'),
            ('[2]', '[toto]'),
            ('[toto]', '[totoro]'),
            ]
        self.assertEqual(results, expected)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRelationToolIOBTreeGraph))
    if USE_RDFLIB:
        suite.addTest(unittest.makeSuite(TestRelationToolRdflibGraph))
    if USE_REDLAND:
        suite.addTest(unittest.makeSuite(TestRelationToolRedlandGraph))
    return suite
