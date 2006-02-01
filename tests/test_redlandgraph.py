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
"""Test Redland Graph
"""

from Products.CPSRelation.tests.CPSRelationTestCase import USE_REDLAND

import os, sys
if __name__ == '__main__' and USE_REDLAND:
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Interface.Verify import verifyClass

if USE_REDLAND:
    # XXX if necessary, RDF has a debug mode:
    #from Products.CPSRelation.redlandgraph import RDF
    #RDF.debug(1)
    from Products.CPSRelation.interfaces.IGraph import IGraph
    from Products.CPSRelation.redlandgraph import RedlandGraph, Model
    from Products.CPSRelation.redlandgraph import Node, Uri, NS
    from Products.CPSRelation.tests.CPSRelationTestCase import RedlandGraphTestCase
    from Products.CPSRelation.tests.CPSRelationTestCase import REDLAND_NAMESPACE
else:
    class RedlandGraphTestCase:
        pass

class TestRedlandGraph(RedlandGraphTestCase):

    def test_interface(self):
        verifyClass(IGraph, RedlandGraph)

    def test_creation(self):
        bindings = {
            "dc": "http://purl.org/dc/elements/1.1/",
            "cps": "http://cps-project.org/2005/data/",
            }
        dummy = RedlandGraph('dummy', backend='memory', bindings=bindings)
        self.assertEqual(dummy.getId(), 'dummy')
        self.assertEqual(dummy.meta_type, 'Redland Graph')
        self.assertEqual(dummy.bindings, bindings)

    def test_test_case_graph(self):
        self.assertEqual(self.graph.getId(), 'rdfgraph')
        self.assertEqual(self.graph.meta_type, 'Redland Graph')
        self.assert_(isinstance(self.graph, RedlandGraph))
        self.assert_(self.hasPart,
                     u'http://cps-project.org/2005/data/hasPart')
        self.assert_(self.isPartOf,
                     u'http://cps-project.org/2005/data/isPartOf')

    def test__getGraph(self):
        self.assert_(isinstance(self.graph._getGraph(), Model))

    def test_parse_file(self):
        test_graph = RedlandGraph('dummy', backend='memory')
        from Products.CPSRelation import tests as here_tests
        input_source = os.path.join(here_tests.__path__[0],
                                    'test_files/rdf_graph.xml')
        test_graph.parse('file:'+input_source, publicID=Uri('y'))
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
        self.assertEqual(test_graph.printAllRelations(), all_relations)

    def test_parse_string(self):
        test_graph = RedlandGraph('dummy', backend='memory')
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
        test_graph.parse(input_source,
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
        self.assertEqual(test_graph.printAllRelations(), all_relations)

    def test_serialize(self):
        serialized = self.graph.serialize()
        # not possible to test xml rendering, it changes every time...
        start = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:cps="http://cps-project.org/2005/data/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">"""
        self.assert_(serialized.startswith(start))
        end = "</rdf:RDF>\n"
        self.assert_(serialized.endswith(end))

    def test_listRelationIds(self):
        self.assertEqual(self.graph.listRelationIds(),
                         [str(self.isPartOf), str(self.hasPart)])

    def test_deleteAllRelations(self):
        self.assertEqual(self.graph.listRelationIds(),
                         [str(self.isPartOf), str(self.hasPart)])
        self.graph.deleteAllRelations()
        self.assertEqual(self.graph.listRelationIds(), [])

    def test_hasRelation(self):
        self.assertEqual(self.graph.hasRelation(self.isPartOf),
                         True)
        self.assertEqual(self.graph.hasRelation(REDLAND_NAMESPACE['isPartOfEuh']),
                         False)

    def test_addRelation(self):
        self.assertEqual(self.graph.listRelationIds(),
                         [str(self.isPartOf), str(self.hasPart)])
        new_relation = REDLAND_NAMESPACE['dummy']
        self.graph.addRelation(new_relation)
        self.assertEqual(self.graph.listRelationIds(),
                         [str(self.isPartOf), str(self.hasPart)])
        # XXX AT: in RDF graph, relation is added only if a relation instance
        # is added...
        self.graph.addRelationFor(Node(Uri('25')), new_relation, Node(Uri('2')))
        self.assertEqual(self.graph.listRelationIds(),
                         [str(self.isPartOf), str(self.hasPart),
                          str(new_relation)])

    def test_deleteRelation(self):
        self.assertEqual(self.graph.listRelationIds(),
                         [str(self.isPartOf), str(self.hasPart)])
        self.graph.deleteRelation(self.isPartOf)
        self.assertEqual(self.graph.listRelationIds(),
                         [str(self.hasPart)])

    def test_listAllRelations(self):
        all_relations = [
            ('[1]', str(self.hasPart), '[10]'),
            ('[2]', str(self.hasPart), '[10]'),
            ('[2]', str(self.hasPart), '[23]'),
            ('[2]', str(self.hasPart), '[25]'),
            ('[10]', str(self.isPartOf), '[1]'),
            ('[10]', str(self.isPartOf), '[2]'),
            ('[23]', str(self.isPartOf), '[2]'),
            ('[25]', str(self.isPartOf), '[2]'),
            ]
        self.assertEqual(self.graph.printAllRelations(), all_relations)

    def test_hasRelationFor(self):
        self.assertEqual(
            self.graph.hasRelationFor(Node(Uri('1')), self.hasPart),
            True)
        self.assertEqual(
            self.graph.hasRelationFor(Node(Uri('3')), self.hasPart),
            False)

    def test_addRelationFor(self):
        self.assertEqual(
            self.graph.hasRelationFor(Node(Uri('3')), self.hasPart),
            False)
        self.graph.addRelationFor(Node(Uri('3')), self.hasPart, Node(Uri('10')))
        self.assertEqual(
            self.graph.hasRelationFor(Node(Uri('3')), self.hasPart),
            True)

    def test_addRelationsFor(self):
        rel = self.graph.getRelationsFor(Node(Uri('10')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[1]', '[2]'))
        new_rel = (
            (Node(Uri('10')), self.isPartOf, Node(Uri('3'))),
            (Node(Uri('10')), self.isPartOf, Node(Uri('23'))),
            )
        self.graph.addRelationsFor(new_rel)
        rel = self.graph.getRelationsFor(Node(Uri('10')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[1]', '[2]', '[3]', '[23]'))
        # XXX inverse relations are not added
        self.assertEqual(
            self.graph.getRelationsFor(Node(Uri('3')), self.hasPart),
            ())
        self.assertEqual(
            self.graph.getRelationsFor(Node(Uri('23')), self.hasPart),
            ())

    def test_deleteRelationFor(self):
        related = self.graph.getRelationsFor(Node(Uri('1')), self.hasPart)
        related = self.makeStringTuple(related)
        self.assertEqual(related, ('[10]',))
        self.graph.deleteRelationFor(Node(Uri('1')), self.hasPart, Node(Uri('10')))
        self.assertEqual(
            self.graph.getRelationsFor(Node(Uri('1')), self.hasPart),
            ())

    def test_deleteRelationsFor(self):
        del_rel = (
            (Node(Uri('1')), self.hasPart, Node(Uri('10'))),
            (Node(Uri('2')), self.hasPart, Node(Uri('23'))),
            )
        self.graph.deleteRelationsFor(del_rel)

        self.assertEqual(
            self.graph.getRelationsFor(Node(Uri('1')), self.hasPart),
            ())
        rel = self.graph.getRelationsFor(Node(Uri('2')), self.hasPart)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[10]', '[25]'))
        # XXX inverse relation is not deleted
        rel = self.graph.getRelationsFor(Node(Uri('10')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[1]', '[2]'))
        rel = self.graph.getRelationsFor(Node(Uri('23')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[2]',))
        rel = self.graph.getRelationsFor(Node(Uri('25')), self.isPartOf)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[2]',))

    def test_deleteRelationsFor_None(self):
        rel = self.graph.getRelationsFor(Node(Uri('1')), self.hasPart)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[10]',))
        rel = self.graph.getRelationsFor(Node(Uri('2')), self.hasPart)
        rel = self.makeStringTuple(rel)
        self.assertEqual(rel, ('[10]', '[23]', '[25]'))

        del_rel = (
            (Node(Uri('1')), self.hasPart, Node(Uri('10'))),
            (Node(Uri('2')), self.hasPart, None),
            )
        self.graph.deleteRelationsFor(del_rel)

        self.assertEqual(
            self.graph.getRelationsFor(Node(Uri('1')), self.hasPart),
            ())
        self.assertEqual(
            self.graph.getRelationsFor(Node(Uri('2')), self.hasPart),
            ())

    def test_getValueFor(self):
        # 1 --hasPart--> 10
        # 2 --hasPart--> 10, 23, 25
        self.assertEqual(
            self.graph.getValueFor(Node(Uri('1')), self.hasPart),
            Node(Uri('10')))
        # test default
        self.assertEqual(
            self.graph.getValueFor(Node(Uri('3')), self.hasPart),
            None)
        self.assertEqual(
            self.graph.getValueFor(Node(Uri('3')), self.hasPart,
                                   default=Node('4')),
            Node('4'))
        # test any
        self.assertEqual(
            self.graph.getValueFor(Node(Uri('1')), self.hasPart, any=False),
            Node(Uri('10')))
        # not possible to know which entry will be returned
        self.assert_(
            self.graph.getValueFor(Node(Uri('2')), self.hasPart, any=True)
            in (Node(Uri('10')), Node(Uri('23')), Node(Uri('25'))))
        self.assertRaises(ValueError,
                          self.graph.getValueFor,
                          Node(Uri('2')),
                          self.hasPart,
                          any=False)

        # test without subject
        self.assertEqual(
            self.graph.getValueFor(None, self.hasPart, Node(Uri('23'))),
            Node(Uri('2')))
        self.assertEqual(
            self.graph.getValueFor(None, self.hasPart, Node(Uri('3'))),
            None)
        self.assertEqual(
            self.graph.getValueFor(None, self.hasPart, Node(Uri('3')),
                                   default=Node(Uri('666'))),
            Node(Uri('666')))
        self.assert_(
            self.graph.getValueFor(None, self.hasPart, Node(Uri('10')),
                                   any=True)
            in (Node(Uri('1')), Node(Uri('2'))))
        self.assertRaises(ValueError,
                          self.graph.getValueFor,
                          None,
                          self.hasPart,
                          Node(Uri('10')),
                          any=False)

        # test without predicate
        self.assertEqual(
            self.graph.getValueFor(Node(Uri('2')), None, Node(Uri('23'))),
            self.hasPart)
        self.assertEqual(
            self.graph.getValueFor(Node(Uri('1')), None, Node(Uri('3'))),
            None)
        self.assertEqual(
            self.graph.getValueFor(Node(Uri('1')), None, Node(Uri('3')),
                                   default=6),
            6)
        self.graph.addRelationFor(Node(Uri('1')), self.isPartOf, Node(Uri('10')))
        self.assert_(
            self.graph.getValueFor(Node(Uri('1')), None, Node(Uri('10')),
                                   any=True)
            in (self.hasPart, self.isPartOf))
        self.assertRaises(ValueError,
                          self.graph.getValueFor,
                          Node(Uri('1')),
                          None,
                          Node(Uri('10')),
                          any=False)

    def test_getRelationsFor(self):
        self.assertEqual(
            self.graph.getRelationsFor(Node(Uri('1')), self.hasPart),
            (Node(Uri('10')),))
        related = self.graph.getRelationsFor(Node(Uri('2')), self.hasPart)
        related = self.makeStringTuple(related)
        self.assertEqual(related, ('[23]', '[25]', '[10]'))

    def test_getInverseRelationsFor(self):
        related = self.graph.getInverseRelationsFor(Node(Uri('10')), self.hasPart)
        related = self.makeStringTuple(related)
        self.assertEqual(related, ('[1]', '[2]'))

    def test_getAllRelationsFor(self):
        self.assertEqual(
            self.graph.getAllRelationsFor(Node(Uri('1'))),
            [(self.hasPart, Node(Uri('10')))])

    def test_getAllInverseRelationsFor(self):
        related = self.graph.getAllInverseRelationsFor(Node(Uri(('10'))))
        expected = [(Node(Uri('1')), self.hasPart),
                    (Node(Uri('2')), self.hasPart),
                    ]
        # XXX AT: dont know why, but sometimes node comparison fails ; use
        # hashes instead
        related = [(hash(x), hash(y)) for (x, y) in related]
        expected = [(hash(x), hash(y)) for (x, y) in expected]
        self.assertEqual(related, expected)

    def test_removeRelationsFor(self):
        related = self.graph.getRelationsFor(Node(Uri('10')), self.isPartOf)
        related = self.makeStringTuple(related)
        self.assertEqual(related, ('[1]', '[2]'))
        self.graph.addRelationFor(Node(Uri('10')), self.hasPart, Node(Uri('666')))
        related = self.graph.getRelationsFor(Node(Uri('10')), self.hasPart)
        related = self.makeStringTuple(related)
        self.assertEqual(related, ('[666]',))
        self.graph.removeRelationsFor(Node(Uri('10')), self.isPartOf)
        self.assertEqual(
            self.graph.getRelationsFor(Node(Uri('10')), self.isPartOf),
            ())
        related = self.graph.getRelationsFor(Node(Uri('10')), self.hasPart)
        related = self.makeStringTuple(related)
        self.assertEqual(related, ('[666]',))

    def test_removeAllRelationsFor(self):
        related = self.graph.getRelationsFor(Node(Uri('10')), self.isPartOf)
        related = self.makeStringTuple(related)
        self.assertEqual(related, ('[1]', '[2]'))
        self.graph.addRelationFor(Node(Uri('10')), self.hasPart, Node(Uri('666')))
        related = self.graph.getRelationsFor(Node(Uri('10')), self.hasPart)
        related = self.makeStringTuple(related)
        self.assertEqual(related, ('[666]',))
        self.graph.removeAllRelationsFor(Node(Uri('10')))
        self.assertEqual(
            self.graph.getRelationsFor(Node(Uri('10')), self.isPartOf),
            ())
        self.assertEqual(
            self.graph.getRelationsFor(Node(Uri('10')), self.hasPart),
            ())

    def test_query(self):
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
        results = self.graph.query(query, query_language='sparql')
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
        results = self.graph.query(query, query_language='sparql')
        results = [(str(x['subj']), str(x['obj'])) for x in results]
        expected = [
            ('[1]', '[totoro]'),
            ('[2]', '[toto]'),
            ('[toto]', '[totoro]'),
            ]
        self.assertEqual(results, expected)

    def test_order(self):
        test_graph = RedlandGraph('dummy', backend='memory')
        # root
        #   section1
        #     subsection11
        #     subsection12
        #   my section 2
        #     another subsection21
        #     a subsection22
        #   section3
        #     subsection 31
        #       subsubsection 311
        self.hasOrder = REDLAND_NAMESPACE['hasOrder']
        self.hasLevel = REDLAND_NAMESPACE['hasLevel']
        test_graph.addRelationFor(Node(Uri('root')), self.hasPart,
                                  Node(Uri('section1')))
        test_graph.addRelationFor(Node(Uri('root')), self.hasLevel, '1')
        test_graph.addRelationFor(Node(Uri('section1')), self.hasOrder, '1')
        test_graph.addRelationFor(Node(Uri('section1')), self.hasLevel, '2')
        test_graph.addRelationFor(Node(Uri('section1')), self.hasPart,
                                  Node(Uri('subsection11')))
        test_graph.addRelationFor(Node(Uri('subsection11')), self.hasOrder, '1')
        test_graph.addRelationFor(Node(Uri('subsection11')), self.hasLevel, '3')
        test_graph.addRelationFor(Node(Uri('section1')), self.hasPart,
                                  Node(Uri('subsection12')))
        test_graph.addRelationFor(Node(Uri('subsection12')), self.hasOrder, '2')
        test_graph.addRelationFor(Node(Uri('subsection12')), self.hasLevel, '3')
        test_graph.addRelationFor(Node(Uri('root')), self.hasPart,
                                  Node(Uri('my section 2')))
        test_graph.addRelationFor(Node(Uri('my section 2')), self.hasOrder, '2')
        test_graph.addRelationFor(Node(Uri('my section 2')), self.hasLevel, '2')
        test_graph.addRelationFor(Node(Uri('my section 2')), self.hasPart,
                                  Node(Uri('another subsection21')))
        test_graph.addRelationFor(Node(Uri('another subsection21')), self.hasOrder, '1')
        test_graph.addRelationFor(Node(Uri('another subsection21')), self.hasLevel, '3')
        test_graph.addRelationFor(Node(Uri('my section 2')), self.hasPart,
                                  Node(Uri('a subsection22')))
        test_graph.addRelationFor(Node(Uri('a subsection22')), self.hasOrder, '2')
        test_graph.addRelationFor(Node(Uri('a subsection22')), self.hasLevel, '3')
        test_graph.addRelationFor(Node(Uri('my section 2')), self.hasOrder, '2')
        test_graph.addRelationFor(Node(Uri('root')), self.hasPart,
                                  Node(Uri('section3')))
        test_graph.addRelationFor(Node(Uri('section3')), self.hasOrder, '3')
        test_graph.addRelationFor(Node(Uri('section3')), self.hasLevel, '2')
        test_graph.addRelationFor(Node(Uri('section3')), self.hasPart,
                                  Node(Uri('subsection31')))
        test_graph.addRelationFor(Node(Uri('subsection31')), self.hasOrder, '1')
        test_graph.addRelationFor(Node(Uri('subsection31')), self.hasLevel, '3')
        test_graph.addRelationFor(Node(Uri('subsection31')), self.hasPart,
                                  Node(Uri('subsubsection311')))
        test_graph.addRelationFor(Node(Uri('subsubsection311')), self.hasOrder, '1')
        test_graph.addRelationFor(Node(Uri('subsubsection311')), self.hasLevel, '4')

        query = """
PREFIX cps: <http://cps-project.org/2005/data/>
SELECT ?subj ?obj
WHERE {
  ?subj cps:hasPart ?obj
  ?obj cps:hasOrder ?order
  ?obj cps:hasLevel ?level
}
ORDER BY ?level ?order
"""
        results = test_graph.query(query, query_language='sparql')
        results = [(str(x['subj']), str(x['obj'])) for x in results]

        expected = [
            ('[root]', '[section1]'),
            ('[root]', '[my section 2]'),
            ('[root]', '[section3]'),
            ('[section1]', '[subsection11]'),
            ('[my section 2]', '[another subsection21]'),
            ('[section3]', '[subsection31]'),
            ('[section1]', '[subsection12]'),
            ('[my section 2]', '[a subsection22]'),
            ('[subsection31]', '[subsubsection311]'),
            ]

        self.assertEqual(results, expected, keep_order=True)


    def test_query_node(self):
        # tests query with a node value, must be a node with namespace
        CPS_NAMESPACE_URI = "http://cps-project.org/2005/data/"
        CPS_NAMESPACE = NS(CPS_NAMESPACE_URI)
        self.graph.addRelationFor(Node(Uri(('1'))), self.hasPart, CPS_NAMESPACE['totoro'])

        query = """
PREFIX cps: <http://cps-project.org/2005/data/>
SELECT ?subj
WHERE {
  ?subj cps:hasPart <totoro> .
}
"""
        results = self.graph.query(query, query_language='sparql',
                                   base_uri=Uri(CPS_NAMESPACE_URI))
        results = [str(x['subj']) for x in results]
        self.assertEqual(results, ['[1]'])


def test_suite():
    suite = unittest.TestSuite()
    if USE_REDLAND:
        suite.addTest(unittest.makeSuite(TestRedlandGraph))
    return suite

if __name__ == '__main__':
    framework()
