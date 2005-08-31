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
"""CPSRelation test case
"""

import unittest

USE_RDF = 0

# XXX check that rdflib is installed before importing
try:
    from rdflib import Namespace, URIRef
except ImportError, err:
    if str(err) != 'No module named rdflib':
        raise
else:
    USE_RDF = 1

from Products.CPSRelation.relationtool import RelationTool

if USE_RDF:
    RDF_NAMESPACE = Namespace('http://cps-project.org/2005/data/')

class CPSRelationTestCase(unittest.TestCase):

    # XXX AT: order is not important in here so override it to sort
    # lists/tuples
    def assertEqual(self, first, second, msg=None):
        if isinstance(first, tuple):
            first_list = list(first)
            first_list.sort()
            first = tuple(first_list)
        elif isinstance(first, list):
            first.sort()
        if isinstance(second, tuple):
            second_list = list(second)
            second_list.sort()
            second = tuple(second_list)
        elif isinstance(second, list):
            second.sort()
        return unittest.TestCase.assertEqual(self, first, second, msg)

    assertEquals = assertEqual

class IOBTreeGraphTestCase(CPSRelationTestCase):
    """CPSRelation test case using IOBtree relations"""

    def setUp(self):
        self.rtool = RelationTool()
        self.rtool.addGraph('iobtreegraph', 'IOBTree Graph')
        self.graph = self.rtool.getGraph('iobtreegraph')
        self.graph.addRelation('hasPart',
                               inverse_id='isPartOf',
                               title='has part')
        self.hasPart = self.graph._getRelation('hasPart')
        self.graph.addRelation('isPartOf',
                               inverse_id='hasPart',
                               title='is part of')
        self.isPartOf = self.graph._getRelation('isPartOf')

        # 1 --hasPart--> 10
        # 2 --hasPart--> 10, 23, 25
        self.hasPart.addRelationFor(1, 10)
        self.hasPart.addRelationFor(2, 10)
        self.hasPart.addRelationFor(2, 23)
        self.hasPart.addRelationFor(2, 25)

    def tearDown(self):
        del self.rtool
        del self.graph
        del self.hasPart
        del self.isPartOf

class RDFGraphTestCase(CPSRelationTestCase):
    """CPSRelation test case using RDF graphs"""

    def setUp(self):
        self.rtool = RelationTool()
        self.rtool.addGraph('rdfgraph', 'RDF Graph')
        self.graph = self.rtool.getGraph('rdfgraph')
        # 2 relations, hasPart and its inverse, isPartOf

        self.hasPart_ns = RDF_NAMESPACE['hasPart']
        self.graph.addRelationFor(URIRef('1'), self.hasPart_ns, URIRef('10'))
        self.graph.addRelationFor(URIRef('2'), self.hasPart_ns, URIRef('10'))
        self.graph.addRelationFor(URIRef('2'), self.hasPart_ns, URIRef('23'))
        self.graph.addRelationFor(URIRef('2'), self.hasPart_ns, URIRef('25'))

        self.isPartOf_ns = RDF_NAMESPACE['isPartOf']
        self.graph.addRelationFor(URIRef('10'), self.isPartOf_ns, URIRef('1'))
        self.graph.addRelationFor(URIRef('10'), self.isPartOf_ns, URIRef('2'))
        self.graph.addRelationFor(URIRef('23'), self.isPartOf_ns, URIRef('2'))
        self.graph.addRelationFor(URIRef('25'), self.isPartOf_ns, URIRef('2'))

    def tearDown(self):
        del self.rtool
        del self.graph

