# Copyright (c) 2004-2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# - M.-A. Darche
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
"""Graph using rdflib RDF Application framework
"""

import os.path
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from AccessControl import ModuleSecurityInfo
from AccessControl import allow_class

from zope.interface import implements

from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.PortalFolder import PortalFolder

from rdflib import Graph
from rdflib.exceptions import UniquenessError
# rdflib imports, unused here but placed here to provide compatible
# imports. other imports may be needed and added here
import rdflib
from rdflib import Namespace, RDF, URIRef, Literal
ModuleSecurityInfo('rdflib').declarePublic('Namespace', 'RDF',
                                           'URIRef', 'Literal')
allow_class(Namespace)
allow_class(RDF)
allow_class(URIRef)
allow_class(Literal)

from Products.CPSRelation.interfaces import IGraph
from Products.CPSRelation.graphregistry import GraphRegistry
from Products.CPSRelation.graphdrawer import GraphDrawer

class RdflibGraph(UniqueObject, PortalFolder):
    """Graph using rdflib RDF Application framework
    """
    meta_type = 'Rdflib Graph'

    security = ClassSecurityInfo()

    implements(IGraph)

    #
    # Properties
    #

    _properties = (
        {'id': 'backend', 'type': 'selection', 'mode': 'w',
         'select_variable': 'supported_backends',
         'label': "Backend",
         },
        {'id': 'bindings', 'type': 'text', 'mode': 'w',
         'label': "Namespace bindings",
         },
        # path is relative to the var directory of the Zope instance
        {'id': 'bdb_path', 'type': 'string', 'mode': 'w',
         'label': "Path towards bdb files (for bdb backend)",
         },
        )
    supported_backends = [
        'ZODB',
        'SleepyCat',
        ]
    # default values
    backend = 'ZODB'
    bindings = {}
    bdb_path = ''

    #
    # API
    #

    def __init__(self, id, backend='ZODB', bindings={}, bdb_path='', **kw):
        """Initialization

        kw are passed to be able to set the backend and other parameters
        """
        self.id = id
        self.backend = backend
        self.bindings = bindings
        if backend == 'SleepyCat':
            # bdb_path is the path towards the directory where BDB files will
            # be kept in the var directory of the Zope instance
            if not bdb_path:
                raise ValueError("Graph %s cannot be created with SleepyCat "
                                 "backend if no path is specified" %(id,))
            else:
                self.bdb_path = bdb_path
        elif backend == 'ZODB':
            self.rdf_graph = Graph(self.backend)
        else:
            raise ValueError("Backend %s not supported "
                             "for graph %s" %(backend, id))

        # bindings
        graph = self._getGraph()
        for k, v in bindings.items():
            graph.bind(k, v)

    security.declarePrivate('_getGraph')
    def _getGraph(self):
        """Get the RDF graph
        """
        if self.backend == 'SleepyCat':
            # XXX AT: check behaviour with multiple access to BDB
            graph = Graph(backend=self.backend)
            dir_path = os.path.join(CLIENT_HOME, self.bdb_path)
            graph.open(dir_path)
        else:
            graph = self.rdf_graph
        return graph

    security.declareProtected(ManagePortal, 'parse')
    def parse(self, source, publicID=None, format="xml"):
        """Parse source into Graph.

        source can either be a string, location, sml.sax.xmlreader.InputSource
        instance.
        Format defaults to xml (AKA rdf/xml).
        The publicID argument is for specifying the logical URI for the case
        that it's different from the physical source URI.
        """
        # XXX AT: make sure this will not add duplicate relations in the graph,
        # or find a way to make it optional
        rdf_graph = self._getGraph()
        # XXX AT: waiting for rdflib to handle the string case
        if (isinstance(source, str)
            and source.startswith("<?xml")):
            from rdflib import plugin
            from rdflib.syntax.parsers import Parser
            from rdflib.StringInputSource import StringInputSource
            parser = plugin.get(format, Parser)()
            input_source = StringInputSource(source)
            if publicID:
                input_source.setPublicId(publicID)
            res = parser.parse(input_source, rdf_graph)
        else:
            res = rdf_graph.parse(source, publicID, format)
        return res

    security.declareProtected(View, 'serialize')
    def serialize(self, destination=None, format='xml', base=None):
        """Serialize the graph to destination

        If destination is None then serialization is returned as string.
        """
        rdf_graph = self._getGraph()
        return rdf_graph.serialize(destination, format, base)

    security.declareProtected(View, 'listRelationIds')
    def listRelationIds(self):
        """List all the existing relations.
        """
        rdf_graph = self._getGraph()
        items = {}
        # XXX AT: this is not uneffecient, optimization required...
        #for item in rdf_graph.predicates():
        #    items[item] = None
        #return items.keys()
        # Is it more efficient???
        try:
            set
        except NameError:
            from sets import Set as set
        predicates = set(rdf_graph.predicates())
        return list(predicates)

    security.declareProtected(ManagePortal, 'deleteAllRelations')
    def deleteAllRelations(self):
        """Delete all the relations.
        """
        rdf_graph = self._getGraph()
        for triple in tuple(rdf_graph.triples((None, None, None))):
            rdf_graph.remove(triple)

    security.declareProtected(View, 'hasRelation')
    def hasRelation(self, relation_id):
        """Does the graph have a relation with the given id?
        """
        rdf_graph = self._getGraph()
        relations = tuple(rdf_graph.triples((None, relation_id, None)))
        if relations:
            return 1
        else:
            return 0

    security.declareProtected(ManagePortal, 'addRelation')
    def addRelation(self, relation_id, **kw):
        """Add a relation with given id to the graph

        This is handled internally by the RDF graph when adding relations so do
        not do anything
        """
        pass

    security.declareProtected(ManagePortal, 'deleteRelation')
    def deleteRelation(self, relation_id):
        """Delete relation with given id from the graph

        All exiting relation instances for this relation will be deleted
        """
        rdf_graph = self._getGraph()
        for triple in tuple(rdf_graph.triples((None, relation_id, None))):
            rdf_graph.remove(triple)

    # relation instances

    security.declareProtected(View, 'listAllRelations')
    def listAllRelations(self):
        """List all existing relation instances
        """
        rdf_graph = self._getGraph()
        items = []
        for s, p, o in rdf_graph.triples((None, None, None)):
            items.append((s, p, o))
        return items

    security.declareProtected(View, 'printAllRelations')
    def printAllRelations(self):
        """Print all existing relation instances
        """
        rdf_graph = self._getGraph()
        items = []
        for s, p, o in rdf_graph.triples((None, None, None)):
            items.append((str(s), str(p), str(o)))
        return items

    security.declareProtected(View, 'hasRelationFor')
    def hasRelationFor(self, uid, relation_id):
        """Does the graph have a relation for the given object uid and the
        given relation type?
        """
        rdf_graph = self._getGraph()
        objects = tuple(rdf_graph.objects(uid, relation_id))
        if objects:
            return 1
        else:
            return 0

    security.declareProtected(View, 'addRelationFor')
    def addRelationFor(self, uid, relation_id, related_uid):
        """Add relation to the given object uid for the given relation type
        """
        rdf_graph = self._getGraph()
        rdf_graph.add((uid, relation_id, related_uid))

    security.declareProtected(View, 'addRelationsFor')
    def addRelationsFor(self, triples_list):
        """Add given relations to the graph

        triples_list items must be like (uid, relation_id, related_uid)
        Useful when it's costly to access the graph.
        """
        rdf_graph = self._getGraph()
        for item in triples_list:
            rdf_graph.add(item)

    security.declareProtected(View, 'deleteRelationFor')
    def deleteRelationFor(self, uid, relation_id, related_uid):
        """Delete relation for the given object uids and the given relation
        type
        """
        rdf_graph = self._getGraph()
        rdf_graph.remove((uid, relation_id, related_uid))

    security.declareProtected(View, 'deleteRelationsFor')
    def deleteRelationsFor(self, triples_list):
        """Delete given relations in the graph

        triples_list items must be like (uid, relation_id, related_uid)
        Useful when it's costly to access the graph.
        """
        rdf_graph = self._getGraph()
        for item in triples_list:
            rdf_graph.remove(item)

    security.declareProtected(View, 'getValueFor')
    def getValueFor(self, uid, relation_id, related_uid=None,
                    default=None, any=False):
        """Get a value for given uid/relation_id, relation_id/related_uid or
        uid/related_uid pair.

        Exactly one of uid, relation_id or related_uid must be None.

        default is the value to be returned if no value is found.

        if any is True, return any value if more than one are found. If any is
        False, raise ValueError.
        """
        rdf_graph = self._getGraph()
        try:
            retval = rdf_graph.value(uid, relation_id, related_uid,
                                     default, any)
        except UniquenessError, err:
            raise ValueError(err)
        return retval

    security.declareProtected(View, 'getRelationsFor')
    def getRelationsFor(self, uid, relation_id):
        """Get relations for the given object uid and the given relation type
        """
        rdf_graph = self._getGraph()
        return tuple(rdf_graph.objects(uid, relation_id))

    security.declareProtected(View, 'getInverseRelationsFor')
    def getInverseRelationsFor(self, uid, relation_id):
        """Get relations for the given object uid and the inverse of the given
        relation type
        """
        rdf_graph = self._getGraph()
        return tuple(rdf_graph.subjects(relation_id, uid))

    security.declareProtected(View, 'getAllRelationsFor')
    def getAllRelationsFor(self, uid):
        """Get the list of all (predicate, object) tuples for given uid
        """
        rdf_graph = self._getGraph()
        return list(rdf_graph.predicate_objects(uid))

    security.declareProtected(View, 'getAllInverseRelationsFor')
    def getAllInverseRelationsFor(self, uid):
        """Get the list of all (subject, predicate) tuples for given uid
        """
        rdf_graph = self._getGraph()
        return list(rdf_graph.subject_predicates(uid))

    security.declareProtected(View, 'removeRelationsFor')
    def removeRelationsFor(self, uid, relation_id):
        """Remove relations for the given object uid and the given relation
        type
        """
        rdf_graph = self._getGraph()
        for object in tuple(rdf_graph.objects(uid, relation_id)):
            rdf_graph.remove((uid, relation_id, object))

    security.declareProtected(View, 'removeAllRelationsFor')
    def removeAllRelationsFor(self, uid):
        """Remove all relations for the given object uid

        This is useful when deleting an object, for instance.
        """
        rdf_graph = self._getGraph()
        for (predicate, object) in tuple(rdf_graph.predicate_objects(uid)):
            rdf_graph.remove((uid, predicate, object))
        for (subject, predicate) in tuple(rdf_graph.subject_predicates(uid)):
            rdf_graph.remove((subject, predicate, uid))

    security.declareProtected(View, 'query')
    def query(self, query_string, **kw):
        """Query the graph
        """
        raise NotImplementedError

    security.declareProtected(View, 'getDrawing')
    def getDrawing(self):
        """Get drawing for this graph
        """
        drawer = GraphDrawer(self)
        ok, res = drawer.getDrawing()
        return ok, res


    #
    # ZMI
    #

    manage_options = (PortalFolder.manage_options[2],) + (
        {'label': "Relations",
         'action': 'manage_editRelations'
         },
        {'label': "Drawing",
         'action': 'manage_drawing'
         },
        {'label': "Overview",
         'action': 'overview'
         },
        ) + PortalFolder.manage_options[3:]

    security.declareProtected(ManagePortal, 'manage_editRelations')
    manage_editRelations = DTMLFile('zmi/rdfgraph_content', globals())

    security.declareProtected(ManagePortal, 'manage_drawing')
    manage_drawing = DTMLFile('zmi/graph_drawing', globals())

    security.declareProtected(ManagePortal, 'overview')
    overview = DTMLFile('zmi/rdflibgraph_overview', globals())

    security.declareProtected(ManagePortal, 'manage_deleteAllRelations')
    def manage_deleteAllRelations(self, REQUEST=None):
        """Delete relations TTW."""
        self.deleteAllRelations()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url()
                                      + '/manage_editRelations'
                                      '?manage_tabs_message=Deleted.')


InitializeClass(RdflibGraph)

# Register to the graph registry
GraphRegistry.register(RdflibGraph)
