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

from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.Expression import Expression

from Products.CPSRelation.tests.CPSRelationTestCase import USE_REDLAND
from Products.CPSRelation.tests.CPSRelationTestCase import CPSRelationTestCase

from Products.CPSRelation.relationtool import RelationTool
from Products.CPSRelation.objectserializertool import ObjectSerializerTool
from Products.CPSRelation.objectserializer import ObjectSerializer

class FakeObject(SimpleItem):

    def __init__(self, id, **kw):
        self.id = id
        # kws are set as attributes
        for k, v in kw.items():
            setattr(self, k, v)

class FakeUrlTool(Folder):
    id = 'portal_url'

    def getPortalObject(self):
        return FakeObject(id="portal")


class TestObjectSerializerTool(CPSRelationTestCase):

    def setUp(self):
        self.root = Folder('root')
        # set them for acquisition pirposes, needed in expressions tests
        self.root._setObject('portal_relations', RelationTool())
        self.root._setObject('portal_url', FakeUrlTool())
        self.root._setObject('portal_serializer', ObjectSerializerTool())

        self.stool = getattr(self.root, 'portal_serializer')

        # test serializer
        self.expr = """python:[
        (getattr(object, 'id'), 'hasTitle', getattr(object, 'title'))
        ]
        """
        ser = ObjectSerializer('serializer', self.expr)
        ser_id = self.stool._setObject('serializer', ser)
        self.serializer = getattr(self.stool, ser_id)

        # test object
        kw = {
            'title': 'Fake Object',
            'number': 666,
            'reference': "azerty",
            }
        self.object = FakeObject('fake_object', **kw)

    def tearDown(self):
        del self.root
        del self.object
        del self.stool
        del self.serializer
        del self.expr

    def test_creation(self):
        stool = ObjectSerializerTool()
        self.assertEqual(stool.getId(), 'portal_serializer')
        self.assertEqual(stool.meta_type, 'Object Serializer Tool')

    def test_test_case_tool(self):
        self.assertNotEqual(self.stool, None)
        self.assertEqual(self.stool.getId(), 'portal_serializer')
        self.assertEqual(self.stool.meta_type, 'Object Serializer Tool')
        self.assert_(isinstance(self.stool, ObjectSerializerTool))

    def test_hasSerializer(self):
        self.assertEqual(self.stool.hasSerializer('serializer'),
                         True)
        self.assertEqual(self.stool.hasSerializer('serializereuh'),
                         False)

    def test_addSerializer(self):
        self.assertEqual(self.stool.hasSerializer('new_serializer'),
                         False)
        new_expr = """python:[
            (getattr(object, 'id'), 'hasTitle', 'My title'),
            (getattr(object, 'id'), 'isTruly', getattr(object, 'title')),
            ]"""
        self.stool.addSerializer('new_serializer', new_expr)
        self.assertEqual(self.stool.hasSerializer('new_serializer'),
                         True)
        self.assertRaises(ValueError,
                          self.stool.addSerializer,
                          'new_serializer',
                          new_expr)
        new_ser = self.stool.getSerializer('new_serializer')
        self.assertEqual(new_ser.getId(), 'new_serializer')
        self.assertEqual(new_ser.serialization_expr, new_expr)

    def test_deleteSerializer(self):
        self.assertEqual(self.stool.hasSerializer('serializer'),
                         True)
        self.stool.deleteSerializer('serializer')
        self.assertEqual(self.stool.hasSerializer('serializer'),
                         False)

    def test_getSerializer(self):
        self.assertEqual(self.stool.getSerializer('serializer'),
                         self.serializer)
        self.assertRaises(AttributeError,
                          self.stool.getSerializer,
                          'serializereuh')

    def test_getSerializationTriples(self):
        expected_triples = [('fake_object', 'hasTitle', 'Fake Object')]
        triples = self.serializer.getSerializationTriples(self.object,
                                                          'serializer')
        self.assertEqual(triples, expected_triples)
        # test with other serializer
        new_expr = """python:[
            (getattr(object, 'id'), 'hasTitle', 'My title'),
            (getattr(object, 'id'), 'isTruly', getattr(object, 'title')),
            ]"""
        self.stool.addSerializer('new_serializer', new_expr)
        expected_triples = [
            ('fake_object', 'hasTitle', 'My title'),
            ('fake_object', 'isTruly', 'Fake Object'),
            ]
        triples = self.serializer.getSerializationTriples(self.object,
                                                          'new_serializer')
        self.assertEqual(triples, expected_triples)

    # XXX AT: theses tests require Redland
    if USE_REDLAND:
        def test_serializeTriples(self):
            from Products.CPSRelation.redlandgraph import Node, Uri, NS
            namespace = NS('http://www.example.org/')
            triples = [
                (Node(Uri('fake_object')), namespace['hasTitle'], 'My title'),
                (Node(Uri('fake_object')), namespace['isTruly'], 'Fake Object'),
                ]
            serialization = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="fake_object">
    <ns0:isTruly xmlns:ns0="http://www.example.org/">Fake Object</ns0:isTruly>
  </rdf:Description>
  <rdf:Description rdf:about="fake_object">
    <ns0:hasTitle xmlns:ns0="http://www.example.org/">My title</ns0:hasTitle>
  </rdf:Description>
</rdf:RDF>
"""
            self.assertEqual(self.stool.serializeTriples(triples),
                             serialization)

        def test_getSerialization(self):
            # XXX make real triples
            new_expr = """python:[
            (Node(Uri(getattr(object, 'id'))),
             NS('http://www.example.org/')['hasTitle'],
             'My title'),
            (Node(Uri(getattr(object, 'id'))),
             NS('http://www.otherexample.org/')['isTruly'],
             getattr(object, 'title')),
            ]"""
            self.serializer.manage_changeProperties(serialization_expr=new_expr)
            expected = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="fake_object">
    <ns0:hasTitle xmlns:ns0="http://www.example.org/">My title</ns0:hasTitle>
  </rdf:Description>
  <rdf:Description rdf:about="fake_object">
    <ns0:isTruly xmlns:ns0="http://www.otherexample.org/">Fake Object</ns0:isTruly>
  </rdf:Description>
</rdf:RDF>
"""
            serialization = self.stool.getSerialization(self.object,
                                                        'serializer')
            self.assertEqual(serialization, expected)

        def test_getMultipleSerialization(self):
            # XXX make real triples
            new_expr = """python:[
            (Node(Uri(getattr(object, 'id'))),
             NS('http://www.example.org/')['hasTitle'],
             'My title'),
            (Node(Uri(getattr(object, 'id'))),
             NS('http://www.example.org/')['isTruly'],
             getattr(object, 'title')),
            ]"""
            self.serializer.manage_changeProperties(serialization_expr=new_expr)
            other_expr = """python:[
            (Node(Uri(getattr(object, 'id'))),
             NS('http://www.otherexample.org/')['hasNumber'],
             str(getattr(object, 'number'))),
            (Node(Uri(getattr(object, 'id'))),
             NS('http://www.otherexample.org/')['hasReference'],
             getattr(object, 'reference')),
            ]"""
            self.stool.addSerializer('new_serializer', other_expr)
            kw = {
                'title': 'Other Fake Object',
                'number': 689,
                'reference': "My reference",
                }
            other_object = FakeObject('other_fake_object', **kw)
            objects_info = [
                (self.object, 'serializer'),
                (other_object, 'new_serializer'),
                ]
            expected = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="other_fake_object">
    <ns0:hasReference xmlns:ns0="http://www.otherexample.org/">My reference</ns0:hasReference>
  </rdf:Description>
  <rdf:Description rdf:about="other_fake_object">
    <ns0:hasNumber xmlns:ns0="http://www.otherexample.org/">689</ns0:hasNumber>
  </rdf:Description>
  <rdf:Description rdf:about="fake_object">
    <ns0:isTruly xmlns:ns0="http://www.example.org/">Fake Object</ns0:isTruly>
  </rdf:Description>
  <rdf:Description rdf:about="fake_object">
    <ns0:hasTitle xmlns:ns0="http://www.example.org/">My title</ns0:hasTitle>
  </rdf:Description>
</rdf:RDF>
"""
            serialization = self.stool.getMultipleSerialization(objects_info)
            self.assertEqual(serialization, expected)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestObjectSerializerTool))
    return suite

if __name__ == '__main__':
    framework()
