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
"""Test IOBTree Relation
"""

import unittest

from zope.interface.verify import verifyClass

from Products.CPSRelation.interfaces.IRelation import IRelation
from Products.CPSRelation.iobtreerelation import IOBTreeRelation
from Products.CPSRelation.tests.CPSRelationTestCase import IOBTreeGraphTestCase

class TestIOBtreeRelation(IOBTreeGraphTestCase):
    """Test IOBTree Relation"""

    def test_interface(self):
        verifyClass(IRelation, IOBTreeRelation)

    def test_creation(self):
        dummy = IOBTreeRelation('dummy',
                                inverse_id='inverse_dummy',
                                title='Dummy relation')
        self.assertEqual(dummy.getId(), 'dummy')
        self.assertEqual(dummy.meta_type, 'IOBTree Relation')
        self.assertEqual(dummy.title_or_id(), 'Dummy relation')
        self.assertEqual(dummy._getInverseRelationId(), 'inverse_dummy')

    def test_test_case_relations(self):
        # hasPart
        self.assertEqual(self.hasPart.getId(), 'hasPart')
        self.assertEqual(self.hasPart.meta_type, 'IOBTree Relation')
        self.assertEqual(self.hasPart.title_or_id(), 'has part')
        self.assertEqual(self.hasPart._getInverseRelationId(), 'isPartOf')
        # isPartOf
        self.assertEqual(self.isPartOf.getId(), 'isPartOf')
        self.assertEqual(self.isPartOf.meta_type, 'IOBTree Relation')
        self.assertEqual(self.isPartOf.title_or_id(), 'is part of')
        self.assertEqual(self.isPartOf._getInverseRelationId(), 'hasPart')

    def test__getInverseRelationId(self):
        self.assertEqual(self.hasPart._getInverseRelationId(), 'isPartOf')
        self.assertEqual(self.isPartOf._getInverseRelationId(), 'hasPart')
        self.graph.addRelation('dummy',
                               inverse_id='',
                               title='Dummy relation')
        dummy = self.graph._getRelation('dummy')
        self.assertRaises(ValueError, dummy._getInverseRelationId)

    def test__getInverseRelation(self):
        self.assertEqual(self.hasPart._getInverseRelation(), self.isPartOf)
        self.assertEqual(self.isPartOf._getInverseRelation(), self.hasPart)
        self.graph.addRelation('dummy',
                               inverse_id='inverse_dummy',
                               title='Dummy relation')
        dummy = self.graph._getRelation('dummy')
        self.assertRaises(AttributeError, dummy._getInverseRelation)
        self.graph.addRelation('inverse_dummy',
                               inverse_id='',
                               title='Dummy inverse relation')
        inverse_dummy = self.graph._getRelation('inverse_dummy')
        self.assertRaises(ValueError, inverse_dummy._getInverseRelation)

    def test_getRelationsFor(self):
        self.assertEqual(self.hasPart.getRelationsFor(1), (10,))
        self.assertEqual(self.hasPart.getRelationsFor(2), (10, 23, 25))
        self.assertEqual(self.isPartOf.getRelationsFor(1), ())
        self.assertEqual(self.isPartOf.getRelationsFor(10), (1, 2))
        self.assertEqual(self.isPartOf.getRelationsFor(23), (2,))
        self.assertEqual(self.isPartOf.getRelationsFor(25), (2,))

    def test_removeRelationsFor(self):
        self.hasPart.removeAllRelationsFor(1)

        self.assertEqual(self.hasPart.getRelationsFor(1), ())
        self.assertEqual(self.hasPart.getRelationsFor(2), (10, 23, 25))
        self.assertEqual(self.isPartOf.getRelationsFor(1), ())
        self.assertEqual(self.isPartOf.getRelationsFor(10), (2,))
        self.assertEqual(self.isPartOf.getRelationsFor(23), (2,))
        self.assertEqual(self.isPartOf.getRelationsFor(25), (2,))

    def test_addRelationFor(self):
        self.isPartOf.addRelationFor(23, 1)

        self.assertEqual(self.hasPart.getRelationsFor(1), (10, 23))
        self.assertEqual(self.hasPart.getRelationsFor(2), (10, 23, 25))
        self.assertEqual(self.isPartOf.getRelationsFor(1), ())
        self.assertEqual(self.isPartOf.getRelationsFor(10), (1, 2))
        self.assertEqual(self.isPartOf.getRelationsFor(23), (2, 1))
        self.assertEqual(self.isPartOf.getRelationsFor(25), (2,))

        self.assertRaises(TypeError,
                          self.isPartOf.addRelationFor,
                          23,
                          'dummy integer')

    def test_deleteRelationFor(self):
        self.hasPart.deleteRelationFor(1, 10)

        self.assertEqual(self.hasPart.getRelationsFor(1), ())
        self.assertEqual(self.hasPart.getRelationsFor(2), (10, 23, 25))
        self.assertEqual(self.isPartOf.getRelationsFor(1), ())
        self.assertEqual(self.isPartOf.getRelationsFor(10), (2,))
        self.assertEqual(self.isPartOf.getRelationsFor(23), (2,))
        self.assertEqual(self.isPartOf.getRelationsFor(25), (2,))

        self.assertRaises(TypeError,
                          self.isPartOf.deleteRelationFor,
                          23,
                          'dummy integer')

    def test_hasRelationFor(self):
        self.assertEqual(self.hasPart.hasRelationFor(1), True)
        self.assertEqual(self.hasPart.hasRelationFor(2), True)
        self.assertEqual(self.hasPart.hasRelationFor(10), False)
        self.assertEqual(self.hasPart.hasRelationFor(23), False)
        self.assertEqual(self.hasPart.hasRelationFor(25), False)
        self.assertEqual(self.hasPart.hasRelationFor(2900), False)
        self.assertEqual(self.isPartOf.hasRelationFor(1), False)
        self.assertEqual(self.isPartOf.hasRelationFor(2), False)
        self.assertEqual(self.isPartOf.hasRelationFor(3), False)
        self.assertEqual(self.isPartOf.hasRelationFor(10), True)
        self.assertEqual(self.isPartOf.hasRelationFor(23), True)
        self.assertEqual(self.isPartOf.hasRelationFor(25), True)

    def test_listRelations(self):
        self.assertEqual(tuple(self.hasPart.listRelationsFor(2)),
                         ((2, (10, 23, 25)),))
        self.assertEqual(tuple(self.isPartOf.listRelationsFor(10)),
                         ((10, (1, 2)),))
        self.assertEqual(tuple(self.hasPart.listRelationsFor()),
                         ((1, (10,)), (2, (10, 23, 25))))
        self.assertEqual(tuple(self.isPartOf.listRelationsFor()),
                         ((10, (1, 2)), (23, (2,)), (25, (2,))))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIOBtreeRelation))
    return suite
