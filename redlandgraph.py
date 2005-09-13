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
# $Id$

"""Graph using the Redland RDF Application Framework
"""

from zLOG import LOG, DEBUG, INFO

import os.path
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from AccessControl import ModuleSecurityInfo
from AccessControl import allow_class

from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.PortalFolder import PortalFolder

from RDF import Storage, HashStorage, Model, Statement
# RDF imports, unused here but placed here to provide compatible
# imports. other imports may be needed and added here
import RDF
from RDF import Parser, Serializer, Query
from RDF import Uri, Node, NS
ModuleSecurityInfo('RDF').declarePublic('Uri', 'Node', 'NS')
allow_class(Uri)
allow_class(Node)
allow_class(NS)

from Products.CPSRelation.interfaces.IGraph import IGraph
from Products.CPSRelation.graphregistry import GraphRegistry

class RedlandGraph(UniqueObject, PortalFolder):
    """Graph using the Redland RDF Application Framework
    """
    __implements__ = (IGraph,)

    meta_type = 'Redland Graph'

    security = ClassSecurityInfo()

    #
    # API
    #

    def __init__(self, id, bindings={}, backend='bdb', path='', **kw):
        """Initialization

        kw are passed to be able to set the backend and other parameters
        """
        self.id = id
        self.backend = backend
        self.bindings = bindings
        if backend == 'bdb':
            # path is the path towards the directory where BDB files will be
            # kept in the var directory of the Zope instance
            if not path:
                raise ValueError("Graph %s cannot be created with bdb "
                                 "backend if no path is specified" %(id,))
            else:
                # path is the path towards the directory where BDB files will be
                self.path = path
        elif backend == 'memory':
            # for tests
            pass
        else:
            raise ValueError("Backend %s not supported "
                             "for graph %s" %(backend, id))

        # bindings
        #graph = self._getGraph()
        #for k, v in bindings.items():
        #    graph.bind(k, v)

    security.declarePrivate('_getGraph')
    def _getGraph(self):
        """Get the RDF graph
        """
        if self.backend == 'bdb':
            storage = getattr(self, '_v_storage', None)
            if storage is None:
                LOG("_getGraph", DEBUG, "rebuilding storage")
                # XXX AT: check behaviour with multiple access to BDB
                dir_path = os.path.join(CLIENT_HOME, self.path)
                storage = HashStorage(dir_path, options="hash-type='bdb'")
                self._v_storage = storage
        elif self.backend == 'memory':
            storage = getattr(self, '_v_storage', None)
            if storage is None:
                LOG("_getGraph", DEBUG, "rebuilding storage")
                options = "new='yes',hash-type='memory',dir='.'"
                storage = Storage(storage_name="hashes",
                                  name=self.id,
                                  options_string=options)
                self._v_storage = storage
        else:
            raise ValueError("Backend %s not supported "
                             "for graph %s" %(self.backend, self.id))

        graph = Model(storage)
        return graph

    security.declareProtected(ManagePortal, 'parse')
    def parse(self, source, publicID=None, format="application/rdf+xml"):
        """Parse source into Graph.

        Returns boolean success or failure
        source can either be a string, location, sml.sax.xmlreader.InputSource
        instance.
        Format defaults to xml (AKA rdf/xml).
        The publicID argument is for specifying the logical URI for the case
        that it's different from the physical source URI.
        """
        rdf_graph = self._getGraph()
        parser = Parser(mime_type=format)
        if isinstance(source, str) and source.startswith('file:'):
            res = parser.parse_into_model(rdf_graph, source,
                                          base_uri=publicID)
        else:
            # XXX AT: A base URI is required when parsing a string
            if publicID is None:
                publicID = Uri('http://cps-project.org/2005/data/')
            res = parser.parse_string_into_model(rdf_graph, source,
                                                 base_uri=publicID)
        return res

    security.declareProtected(View, 'serialize')
    def serialize(self, destination=None, format="application/rdf+xml", base=None):
        """Serialize the graph to destination

        If destination is None then serialization is returned as string.
        """
        rdf_graph = self._getGraph()
        serializer = Serializer(mime_type=format)
        if destination is None:
            res = serializer.serialize_model_to_string(rdf_graph, base_uri=base)
        else:
            res = serialize_model_to_file(destination, rdf_graph, base_uri=base)
        return res

    security.declareProtected(View, 'listRelationIds')
    def listRelationIds(self):
        """List all the existing relations.
        """
        rdf_graph = self._getGraph()
        relations = {}
        related_statement = Statement(None, None, None)
        related_iter = rdf_graph.find_statements(related_statement)
        while not related_iter.end():
            statement = related_iter.current()
            relations[str(statement.predicate)] = None
            related_iter.next()
        return relations.keys()

    security.declareProtected(ManagePortal, 'deleteAllRelations')
    def deleteAllRelations(self):
        """Delete all the relations.
        """
        rdf_graph = self._getGraph()
        # XXX AT: probably an easier way to do that
        related_statement = Statement(None, None, None)
        related_iter = rdf_graph.find_statements(related_statement)
        while not related_iter.end():
            statement = related_iter.current()
            rdf_graph.remove_statement(statement)
            related_iter.next()

    security.declareProtected(View, 'hasRelation')
    def hasRelation(self, relation_id):
        """Does the graph have a relation with the given id?
        """
        rdf_graph = self._getGraph()
        related_statement = Statement(None, relation_id, None)
        related_iter = rdf_graph.find_statements(related_statement)
        if not related_iter.end():
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
        related_statement = Statement(None, relation_id, None)
        related_iter = rdf_graph.find_statements(related_statement)
        while not related_iter.end():
            statement = related_iter.current()
            rdf_graph.remove_statement(statement)
            related_iter.next()

    # relation instances

    security.declareProtected(View, 'listAllRelations')
    def listAllRelations(self):
        """List all existing relation instances

        This may be only useful for test/debug purposes
        """
        rdf_graph = self._getGraph()
        items = []
        related_statement = Statement(None, None, None)
        related_iter = rdf_graph.find_statements(related_statement)
        while not related_iter.end():
            statement = related_iter.current()
            triple = (str(statement.subject),
                      str(statement.predicate),
                      str(statement.object))
            items.append(triple)
            related_iter.next()
        return items

    security.declareProtected(View, 'hasRelationFor')
    def hasRelationFor(self, uid, relation_id):
        """Does the graph have a relation for the given object uid and the
        given relation type?
        """
        rdf_graph = self._getGraph()
        object = rdf_graph.get_target(uid, relation_id)
        if object is None:
            return 0
        else:
            return 1

    security.declareProtected(View, 'addRelationFor')
    def addRelationFor(self, uid, relation_id, related_uid):
        """Add relation to the given object uid for the given relation type
        """
        rdf_graph = self._getGraph()
        rdf_graph.append(Statement(uid, relation_id, related_uid))

    security.declareProtected(View, 'addRelationsFor')
    def addRelationsFor(self, triplets_list):
        """Add given relations to the graph

        triplets_list items must be like (uid, relation_id, related_uid)
        Useful when it's costly to access the graph.
        """
        rdf_graph = self._getGraph()
        for item in triplets_list:
            rdf_graph.append(Statement(item[0], item[1], item[2]))

    security.declareProtected(View, 'deleteRelationFor')
    def deleteRelationFor(self, uid, relation_id, related_uid):
        """Delete relation for the given object uids and the given relation
        type
        """
        rdf_graph = self._getGraph()
        rdf_graph.remove_statement(Statement(uid, relation_id, related_uid))

    security.declareProtected(View, 'deleteRelationsFor')
    def deleteRelationsFor(self, triplets_list):
        """Delete given relations in the graph

        triplets_list items must be like (uid, relation_id, related_uid)
        Useful when it's costly to access the graph.
        """
        rdf_graph = self._getGraph()
        for item in triplets_list:
            rdf_graph.remove_statement(Statement(item[0], item[1], item[2]))

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
        retval = default
        if related_uid is None:
            assert uid is not None
            assert relation_id is not None
            if any is True:
                retval = rdf_graph.get_target(uid, relation_id)
            else:
                values = rdf_graph.get_targets(uid, relation_id)
        if uid is None:
            assert relation_id is not None
            assert related_uid is not None
            if any is True:
                retval = rdf_graph.get_source(relation_id, related_uid)
            else:
                values = rdf_graph.get_sources(relation_id, related_uid)
        if relation_id is None:
            assert uid is not None
            assert related_uid is not None
            if any is True:
                retval = rdf_graph.get_predicate(uid, related_uid)
            else:
                values = rdf_graph.get_predicates(uid, related_uid)

        # Try to extract only one value is 'any' is False
        if any is False:
            if values.end():
                retval = default
            else:
                retval = values.current()
                next = values.next()
                if not values.end():
                    all_values = [retval, next] + list(values)
                    all_values = [str(x) for x in all_values]
                    err = ("Uniqueness assumption is not fulfilled. "
                           "Multiple values are: %s" % (all_values,))
                    raise ValueError(err)

        return retval

    security.declareProtected(View, 'getRelationsFor')
    def getRelationsFor(self, uid, relation_id):
        """Get relations for the given object uid and the given relation type
        """
        rdf_graph = self._getGraph()
        res = tuple(rdf_graph.get_targets(uid, relation_id))
        return res

    security.declareProtected(View, 'getInverseRelationsFor')
    def getInverseRelationsFor(self, uid, relation_id):
        """Get relations for the given object uid and the inverse of the given
        relation type
        """
        rdf_graph = self._getGraph()
        return tuple(rdf_graph.get_sources(relation_id, uid))

    security.declareProtected(View, 'removeRelationsFor')
    def removeRelationsFor(self, uid, relation_id):
        """Remove relations for the given object uid and the given relation
        type
        """
        rdf_graph = self._getGraph()
        related_statement = Statement(uid, relation_id, None)
        related_iter = rdf_graph.find_statements(related_statement)
        while not related_iter.end():
            rdf_graph.remove_statement(related_iter.current())
            related_iter.next()

    security.declareProtected(View, 'removeAllRelationsFor')
    def removeAllRelationsFor(self, uid):
        """Remove all relations for the given object uid

        This is useful when deleting an object, for instance.
        """
        rdf_graph = self._getGraph()
        # as subject
        related_statement = Statement(uid, None, None)
        related_iter = rdf_graph.find_statements(related_statement)
        while not related_iter.end():
            rdf_graph.remove_statement(related_iter.current())
            related_iter.next()
        # as object
        related_statement = Statement(None, None, uid)
        related_iter = rdf_graph.find_statements(related_statement)
        while not related_iter.end():
            rdf_graph.remove_statement(related_iter.current())
            related_iter.next()

    security.declareProtected(View, 'query')
    def query(self, query_string, base_uri=None,
              query_language='rdql', query_uri=None, **kw):
        """Query the graph

        query_language can either be rdql or sparql
        """
        rdf_graph = self._getGraph()
        query = Query(query_string, base_uri, query_language, query_uri)
        results = list(rdf_graph.execute(query))
        return results

    #
    # ZMI
    #

    manage_options = (
        {'label': "Relations",
         'action': 'manage_editRelations'
         },
        # XXX AT: doc not ready yet
        #{'label': "Overview",
        # 'action': 'overview'
        # },
        ) + PortalFolder.manage_options[2:]

    security.declareProtected(ManagePortal, 'manage_editRelations')
    manage_editRelations = DTMLFile('zmi/rdfgraph_content', globals())

    security.declareProtected(ManagePortal, 'overview')
    overview = DTMLFile('zmi/rdfgraph_overview', globals())

    security.declareProtected(ManagePortal, 'manage_deleteAllRelations')
    def manage_deleteAllRelations(self, REQUEST=None):
        """Delete relations TTW."""
        self.deleteAllRelations()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url()
                                      + '/manage_editRelations'
                                      '?manage_tabs_message=Deleted.')


InitializeClass(RedlandGraph)

# Register to the graph registry
GraphRegistry.register(RedlandGraph)
