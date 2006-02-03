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
#-------------------------------------------------------------------------------
"""Test IOBTree Graph
"""

import unittest
from Interface.Verify import verifyClass

from Products.CPSRelation.interfaces.IGraph import IGraph
from Products.CPSRelation.iobtreegraph import IOBTreeGraph
from Products.CPSRelation.tests.CPSRelationTestCase import IOBTreeGraphTestCase

class TestIOBTreeGraph(IOBTreeGraphTestCase):

    def test_interface(self):
        verifyClass(IGraph, IOBTreeGraph)

    def test_creation(self):
        dummy = IOBTreeGraph('dummy')
        self.assertEqual(dummy.getId(), 'dummy')
        self.assertEqual(dummy.meta_type, 'IOBTree Graph')

    def test_test_case_graph(self):
        self.assertEqual(self.graph.getId(), 'iobtreegraph')
        self.assertEqual(self.graph.meta_type, 'IOBTree Graph')
        self.assert_(isinstance(self.graph, IOBTreeGraph))

    def test__getRelations(self):
        self.assertEqual(self.graph._getRelations(),
                         [self.hasPart, self.isPartOf])

    def test__getRelation(self):
        self.assertEqual(self.graph._getRelation('hasPart'),
                         self.hasPart)
        self.assertEqual(self.graph._getRelation('isPartOf'),
                         self.isPartOf)

    def test_listRelationIds(self):
        self.assertEqual(self.graph.listRelationIds(),
                         ['hasPart', 'isPartOf'])

    def test_deleteAllRelations(self):
        self.assertEqual(self.graph.listRelationIds(),
                         ['hasPart', 'isPartOf'])
        self.graph.deleteAllRelations()
        self.assertEqual(self.graph.listRelationIds(), [])

    def test_hasRelation(self):
        self.assertEqual(self.graph.hasRelation('isPartOf'),
                         True)
        self.assertEqual(self.graph.hasRelation('isPartOfEuh'),
                         False)

    def test_addRelation(self):
        self.assertEqual(self.graph.listRelationIds(),
                         ['hasPart', 'isPartOf'])
        self.graph.addRelation('dummy')
        self.assertEqual(self.graph.listRelationIds(),
                         ['hasPart', 'isPartOf', 'dummy'])

    def test_deleteRelation(self):
        self.assertEqual(self.graph.listRelationIds(),
                         ['hasPart', 'isPartOf'])
        self.graph.deleteRelation('isPartOf')
        self.assertEqual(self.graph.listRelationIds(),
                         ['hasPart'])

    def test_listAllRelations(self):
        all_relations = [
            (1, 'hasPart', 10),
            (2, 'hasPart', 10),
            (2, 'hasPart', 23),
            (2, 'hasPart', 25),
            (10, 'isPartOf', 1),
            (10, 'isPartOf', 2),
            (23, 'isPartOf', 2),
            (25, 'isPartOf', 2),
            ]
        self.assertEqual(self.graph.listAllRelations(),
                         all_relations)

    def test_printAllRelations(self):
        all_relations = [
            ('1', 'hasPart', '10'),
            ('2', 'hasPart', '10'),
            ('2', 'hasPart', '23'),
            ('2', 'hasPart', '25'),
            ('10', 'isPartOf', '1'),
            ('10', 'isPartOf', '2'),
            ('23', 'isPartOf', '2'),
            ('25', 'isPartOf', '2'),
            ]
        self.assertEqual(self.graph.printAllRelations(),
                         all_relations)

    def test_hasRelationFor(self):
        self.assertEqual(self.graph.hasRelationFor(1, 'hasPart'),
                         True)
        self.assertEqual(self.graph.hasRelationFor(3, 'hasPart'),
                         False)

    def test_addRelationFor(self):
        self.assertEqual(self.graph.hasRelationFor(3, 'hasPart'),
                         False)
        self.graph.addRelationFor(3, 'hasPart', 10)
        self.assertEqual(self.graph.hasRelationFor(3, 'hasPart'),
                         True)

    def test_addRelationsFor(self):
        self.assertEqual(self.graph.getRelationsFor(10, 'isPartOf'),
                         (1, 2))
        self.assertEqual(self.graph.getRelationsFor(3, 'hasPart'),
                         ())
        self.assertEqual(self.graph.getRelationsFor(23, 'hasPart'),
                         ())
        new_rel = (
            (10, 'isPartOf', 3),
            (10, 'isPartOf', 23),
            )
        self.graph.addRelationsFor(new_rel)
        self.assertEqual(self.graph.getRelationsFor(10, 'isPartOf'),
                         (1, 2, 3, 23))
        self.assertEqual(self.graph.getRelationsFor(3, 'hasPart'),
                         (10,))
        self.assertEqual(self.graph.getRelationsFor(23, 'hasPart'),
                         (10,))

    def test_deleteRelationFor(self):
        self.assertEqual(self.graph.getRelationsFor(1, 'hasPart'),
                         (10,))
        self.graph.deleteRelationFor(1, 'hasPart', 10)
        self.assertEqual(self.graph.getRelationsFor(1, 'hasPart'),
                         ())

    def test_deleteRelationsFor(self):
        self.assertEqual(self.graph.getRelationsFor(1, 'hasPart'),
                         (10,))
        self.assertEqual(self.graph.getRelationsFor(2, 'hasPart'),
                         (10, 23, 25,))
        del_rel = (
            (1, 'hasPart', 10),
            (2, 'hasPart', 23)
            )
        self.graph.deleteRelationsFor(del_rel)
        self.assertEqual(self.graph.getRelationsFor(1, 'hasPart'),
                         ())
        self.assertEqual(self.graph.getRelationsFor(2, 'hasPart'),
                         (10, 25,))

    def test_getValueFor(self):
        # 1 --hasPart--> 10
        # 2 --hasPart--> 10, 23, 25
        self.assertEqual(self.graph.getValueFor(1, 'hasPart'), 10)
        # test default
        self.assertEqual(self.graph.getValueFor(3, 'hasPart'), None)
        self.assertEqual(self.graph.getValueFor(3, 'hasPart', default=4), 4)
        # test any
        self.assertEqual(self.graph.getValueFor(1, 'hasPart', any=False), 10)
        # not possible to know which entry will be returned
        self.assert_(self.graph.getValueFor(2, 'hasPart', any=True)
                     in (10, 23, 25))
        self.assertRaises(ValueError,
                          self.graph.getValueFor,
                          2,
                          'hasPart',
                          any=False)

        # test without subject
        self.assertEqual(self.graph.getValueFor(None, 'hasPart', 23), 2)
        # test default
        self.assertEqual(self.graph.getValueFor(None, 'hasPart', 3), None)
        self.assertEqual(self.graph.getValueFor(None, 'hasPart', 3, default=4),
                         4)
        # test any
        self.assertEqual(self.graph.getValueFor(None, 'hasPart', 23, any=False),
                         2)
        # not possible to know which entry will be returned
        self.assert_(self.graph.getValueFor(None, 'hasPart', 10, any=True)
                     in (1, 2))
        self.assertRaises(ValueError,
                          self.graph.getValueFor,
                          None,
                          'hasPart',
                          10,
                          any=False)

        # test without predicate
        self.assertRaises(NotImplementedError,
                          self.graph.getValueFor,
                          1,
                          None,
                          10)

    def test_getRelationsFor(self):
        self.assertEqual(self.graph.getRelationsFor(1, 'hasPart'),
                         (10,))
        self.assertEqual(self.graph.getRelationsFor(2, 'hasPart'),
                         (10, 23, 25))

    def test_getInverseRelationsFor(self):
        self.assertEqual(self.graph.getInverseRelationsFor(10, 'hasPart'),
                         (1, 2))

    def test_getAllRelationsFor(self):
        self.assertEqual(self.graph.getAllRelationsFor(1),
                         [('hasPart', 10)])
        self.assertEqual(self.graph.getAllRelationsFor(2),
                         [('hasPart', 10),
                          ('hasPart', 23),
                          ('hasPart', 25),
                          ])

    def test_getAllInverseRelationsFor(self):
        self.assertEqual(self.graph.getAllInverseRelationsFor(10),
                         [(1, 'hasPart'),
                          (2, 'hasPart'),
                          ])

    def test_removeRelationsFor(self):
        self.assertEqual(self.graph.getRelationsFor(10, 'isPartOf'),
                         (1, 2))
        self.graph.addRelationFor(10, 'hasPart', 666)
        self.assertEqual(self.graph.getRelationsFor(10, 'hasPart'),
                         (666,))
        self.graph.removeRelationsFor(10, 'isPartOf')
        self.assertEqual(self.graph.getRelationsFor(10, 'isPartOf'),
                         ())
        self.assertEqual(self.graph.getRelationsFor(10, 'hasPart'),
                         (666,))

    def test_removeAllRelationsFor(self):
        self.assertEqual(self.graph.getRelationsFor(10, 'isPartOf'),
                         (1, 2))
        self.graph.addRelationFor(10, 'hasPart', 666)
        self.assertEqual(self.graph.getRelationsFor(10, 'hasPart'),
                         (666,))
        self.graph.removeAllRelationsFor(10)
        self.assertEqual(self.graph.getRelationsFor(10, 'isPartOf'),
                         ())
        self.assertEqual(self.graph.getRelationsFor(10, 'hasPart'),
                         ())

    def test_query(self):
        self.assertRaises(NotImplementedError,
                          self.graph.query,
                          'query :)')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIOBTreeGraph))
    return suite
