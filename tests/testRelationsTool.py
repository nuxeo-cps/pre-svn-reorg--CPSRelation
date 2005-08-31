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

class TestRelationsTool(CPSRelationTestCase.CPSRelationTestCase):
    """Test Relations Tool"""

    def test_tool_presence(self):
        self.assertNotEqual(self.rtool, None)

    def test_getRelations(self):
        portal_relations_list = self.rtool._getRelations()
        self.assertEquals(len(portal_relations_list), 2)

    def test_getRelation(self):
        self.assertNotEqual(self.rtool._getRelation('hasPart'), None)
        self.assertNotEqual(self.rtool._getRelation('isPartOf'), None)
        self.assertRaises(AttributeError,
                          self.rtool._getRelation,
                          'dummy')

    def test_getRelationIds(self):
        relations_list = ['isPartOf', 'hasPart']
        relations_list.sort()
        portal_relations_list = self.rtool._getRelationIds()
        portal_relations_list.sort()
        self.assertEquals(portal_relations_list, relations_list)

    def test_hasRelation(self):
        self.assertEqual(self.rtool.hasRelation('hasPart'), True)
        self.assertEqual(self.rtool.hasRelation('isPartOf'), True)
        self.assertEqual(self.rtool.hasRelation('dummy'), False)

    def test_addRelation(self):
        self.assertRaises(ValueError,
                          self.rtool.addRelation,
                          id='isPartOf',
                          inverse_id='hasPart',
                          title='is part of')
        self.assertEqual(self.rtool.hasRelation('dummy'), False)
        self.rtool.addRelation('dummy',
                               inverse_id='',
                               title='dummy relation')
        self.assertEqual(self.rtool.hasRelation('dummy'), True)

    def test_hasRelationFor(self):
        self.assertEqual(self.rtool.hasRelationFor(1, 'hasPart'), True)
        self.assertEqual(self.rtool.hasRelationFor(10, 'hasPart'), False)

    def test_getRelationFor(self):
        self.assertEqual(self.rtool.getRelationFor(1, 'hasPart'), (10,))
        self.assertEqual(self.rtool.getRelationFor(2, 'hasPart'), (10, 23, 25))
        self.assertEqual(self.rtool.getRelationFor(10, 'isPartOf'), (1, 2))
        self.assertEqual(self.rtool.getRelationFor(23, 'isPartOf'), (2,))
        self.assertEqual(self.rtool.getRelationFor(25, 'isPartOf'), (2,))

    def test_addRelationFor(self):
        self.assertEqual(self.rtool.getRelationFor(10, 'isPartOf'), (1, 2))

        self.rtool.addRelationFor(10, 'isPartOf', 3)

        self.assertEqual(self.rtool.getRelationFor(10, 'isPartOf'), (1, 2, 3))
        self.assertEqual(self.rtool.getRelationFor(3, 'hasPart'), (10,))

    def test_delRelationFor(self):
        self.rtool.deleteRelationFor(1, 'hasPart', 10)

        self.assertEqual(self.rtool.getRelationFor(1, 'hasPart'), ())
        self.assertEqual(self.rtool.getRelationFor(2, 'hasPart'), (10, 23, 25))
        self.assertEqual(self.rtool.getRelationFor(10, 'isPartOf'), (2,))
        self.assertEqual(self.rtool.getRelationFor(23, 'isPartOf'), (2,))
        self.assertEqual(self.rtool.getRelationFor(25, 'isPartOf'), (2,))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRelationsTool))
    return suite

if __name__ == '__main__':
    framework()
