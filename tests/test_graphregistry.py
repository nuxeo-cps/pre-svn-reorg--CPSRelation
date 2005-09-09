#!/usr/bin/python
# Copyright (c) 2005 Nuxeo SARL <http://nuxeo.com>
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
"""Graph registry tests
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest

from Products.CPSRelation.tests.CPSRelationTestCase import USE_RDFLIB
from Products.CPSRelation.tests.CPSRelationTestCase import USE_REDLAND

from Products.CPSRelation.graphregistry import GraphRegistry
from Products.CPSRelation.iobtreegraph import IOBTreeGraph
if USE_RDFLIB:
    from Products.CPSRelation.rdfgraph import RDFGraph
if USE_REDLAND:
    from Products.CPSRelation.redlandgraph import RedlandGraph
from Products.CPSRelation.tests.CPSRelationTestCase import CPSRelationTestCase

# default graph types registered at product setup. To be modified when adding
# new graph types
DEFAULT_GRAPH_TYPES = [
    IOBTreeGraph.meta_type,
    ]
if USE_RDFLIB:
    DEFAULT_GRAPH_TYPES.append(RDFGraph.meta_type)
if USE_REDLAND:
    DEFAULT_GRAPH_TYPES.append(RedlandGraph.meta_type)

class DummyGraph:
    meta_type = 'Dummy Graph'

class TestGraphRegistry(CPSRelationTestCase):

    def setUp(self):
        self.save_graph_classes = GraphRegistry._graph_classes.copy()

    def tearDown(self):
        GraphRegistry._graph_classes = self.save_graph_classes

    def test_listGraphTypes(self):
        graph_types = DEFAULT_GRAPH_TYPES
        self.assertEquals(GraphRegistry.listGraphTypes(), graph_types)

    def test_register(self):
        GraphRegistry.register(DummyGraph)
        graph_types = DEFAULT_GRAPH_TYPES + ['Dummy Graph']
        self.assertEquals(GraphRegistry.listGraphTypes(), graph_types)

    def test_makeIOBTreeGraph(self):
        graph = GraphRegistry.makeGraph(IOBTreeGraph.meta_type,
                                        'test_iobtreegraph')
        self.assertEquals(graph.meta_type, IOBTreeGraph.meta_type)
        self.assertEquals(graph.getId(), 'test_iobtreegraph')
        self.assert_(isinstance(graph, IOBTreeGraph))

    def test_makeRDFGraph(self):
        if not USE_RDFLIB:
            return
        graph = GraphRegistry.makeGraph(RDFGraph.meta_type,
                                        'test_rdfgraph')
        self.assertEquals(graph.meta_type, RDFGraph.meta_type)
        self.assertEquals(graph.getId(), 'test_rdfgraph')
        self.assert_(isinstance(graph, RDFGraph))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGraphRegistry))
    return suite

if __name__ == '__main__':
    framework()
