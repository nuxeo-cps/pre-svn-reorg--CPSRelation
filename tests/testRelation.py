#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
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
import CPSRelationTestCase

from Products.CPSRelation.Relation import Relation

class TestRelation(CPSRelationTestCase.CPSRelationTestCase):
    """Test Relation"""

    def test_relation_creation(self):
        dummy = Relation('dummy',
                         inverse_id='inverse_dummy',
                         title='Dummy relation')
        self.assertEqual(dummy.getId(), 'dummy')
        self.assertEqual(dummy.title_or_id(), 'Dummy relation')
        self.assertEqual(dummy._getInverseRelationId(), 'inverse_dummy')

    def test_getInverseRelationId(self):
        self.assertEqual(self.hasPart._getInverseRelationId(), 'isPartOf')
        self.assertEqual(self.isPartOf._getInverseRelationId(), 'hasPart')
        self.rtool.addRelation('dummy',
                               inverse_id='',
                               title='Dummy relation')
        dummy = self.rtool._getRelation('dummy')
        self.assertRaises(ValueError, dummy._getInverseRelationId)

    def test_getInverseRelation(self):
        self.assertEqual(self.hasPart._getInverseRelation(), self.isPartOf)
        self.assertEqual(self.isPartOf._getInverseRelation(), self.hasPart)
        self.rtool.addRelation('dummy',
                               inverse_id='inverse_dummy',
                               title='Dummy relation')
        dummy = self.rtool._getRelation('dummy')
        self.assertRaises(AttributeError, dummy._getInverseRelation)
        self.rtool.addRelation('inverse_dummy',
                               inverse_id='',
                               title='Dummy inverse relation')
        inverse_dummy = self.rtool._getRelation('inverse_dummy')
        self.assertRaises(ValueError, inverse_dummy._getInverseRelation)

    def test_getRelationFor(self):
        self.assertEqual(self.hasPart.getRelationFor(1), (10,))
        self.assertEqual(self.hasPart.getRelationFor(2), (10, 23, 25))
        self.assertEqual(self.isPartOf.getRelationFor(1), ())
        self.assertEqual(self.isPartOf.getRelationFor(10), (1, 2))
        self.assertEqual(self.isPartOf.getRelationFor(23), (2,))
        self.assertEqual(self.isPartOf.getRelationFor(25), (2,))

    def test_removeRelationFor(self):
        self.hasPart.removeRelationFor(1)

        self.assertEqual(self.hasPart.getRelationFor(1), ())
        self.assertEqual(self.hasPart.getRelationFor(2), (10, 23, 25))
        self.assertEqual(self.isPartOf.getRelationFor(1), ())
        self.assertEqual(self.isPartOf.getRelationFor(10), (2,))
        self.assertEqual(self.isPartOf.getRelationFor(23), (2,))
        self.assertEqual(self.isPartOf.getRelationFor(25), (2,))

    def test_addRelationFor(self):
        self.isPartOf.addRelationFor(23, 1)

        self.assertEqual(self.hasPart.getRelationFor(1), (10, 23))
        self.assertEqual(self.hasPart.getRelationFor(2), (10, 23, 25))
        self.assertEqual(self.isPartOf.getRelationFor(1), ())
        self.assertEqual(self.isPartOf.getRelationFor(10), (1, 2))
        self.assertEqual(self.isPartOf.getRelationFor(23), (2, 1))
        self.assertEqual(self.isPartOf.getRelationFor(25), (2,))

        self.assertRaises(TypeError,
                          self.isPartOf.addRelationFor,
                          23,
                          'dummy integer')

    def test_deleteRelationFor(self):
        self.hasPart.deleteRelationFor(1, 10)

        self.assertEqual(self.hasPart.getRelationFor(1), ())
        self.assertEqual(self.hasPart.getRelationFor(2), (10, 23, 25))
        self.assertEqual(self.isPartOf.getRelationFor(1), ())
        self.assertEqual(self.isPartOf.getRelationFor(10), (2,))
        self.assertEqual(self.isPartOf.getRelationFor(23), (2,))
        self.assertEqual(self.isPartOf.getRelationFor(25), (2,))

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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRelation))
    return suite

if __name__ == '__main__':
    framework()
