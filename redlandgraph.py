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
"""Graph using the Redland RDF Application Framework
"""

import os
import os.path
import tempfile
import string
import logging

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
from RDF import RedlandError
from RDF import Parser, Serializer, Query
from RDF import Uri, Node, NS
ModuleSecurityInfo('RDF').declarePublic('Uri', 'Node', 'NS')
allow_class(Uri)
allow_class(Node)
allow_class(NS)

from Products.CPSRelation.interfaces.IGraph import IGraph
from Products.CPSRelation.graphregistry import GraphRegistry
from Products.CPSRelation.graphdrawer import GraphDrawer

logger = logging.getLogger("CPSRelation.RedlandGraph")

class RedlandGraph(UniqueObject, PortalFolder):
    """Graph using the Redland RDF Application Framework
    """
    __implements__ = (IGraph,)

    meta_type = 'Redland Graph'

    security = ClassSecurityInfo()

    #
    # Properties
    #

    _properties = (
        {'id': 'backend', 'type': 'selection', 'mode': 'w',
         'select_variable': 'supported_backends',
         'label': "Backend",
         },
        {'id': 'bindings', 'type': 'text', 'mode': 'r',
         'label': "Namespace bindings",
         },
        # path is relative to the var directory of the Zope instance
        {'id': 'bdb_path', 'type': 'string', 'mode': 'w',
         'label': "Path towards bdb files (for bdb backend)",
         },
        # mysql options are like
        # host='localhost',port=3306,user='root',password='mypass'
        {'id': 'mysql_options', 'type': 'string', 'mode': 'w',
         'label': "mysql connection parameters (for mysql backend)"
         },
        )
    supported_backends = [
        'memory',
        'bdb',
        'mysql',
        ]
    # default values
    backend = 'memory'
    bindings = {}
    bdb_path = ''
    mysql_options = ''

    #
    # API
    #

    def __init__(self, id, backend='memory', bindings={}, **kw):
        """Initialization

        kw are passed to be able to set the backend specific parameters
        """
        # check backend before init
        if backend not in self.supported_backends:
            raise ValueError("Backend %s not supported "
                             "for graph %s" %(backend, id))

        self.id = id
        self.backend = backend
        if backend == 'bdb':
            # path is the path towards the directory where BDB files will be
            # kept in the var directory of the Zope instance
            bdb_path = kw.get('bdb_path')
            if not bdb_path:
                raise ValueError("Graph %s cannot be created with bdb "
                                 "backend if no bdb_path is specified" %(id,))
            else:
                self.bdb_path = bdb_path
        elif backend == 'mysql':
            # options information
            mysql_options = kw.get('mysql_options')
            if not mysql_options:
                raise ValueError("Graph %s cannot be created with mysql "
                                 "backend if no mysql_options are specified" %(id,))
            else:
                self.mysql_options = mysql_options
        self.bindings = bindings

    security.declarePrivate('_getGraph')
    def _getGraph(self):
        """Get the RDF graph
        """
        if self.backend == 'memory':
            storage = getattr(self, '_v_storage', None)
            if storage is None:
                # WARNING level because content can be lost with memory storage
                logger.warn("_getGraph: rebuilding memory storage")
                options = "new='yes',hash-type='memory',dir='.'"
                storage = Storage(storage_name="hashes",
                                  name=self.id,
                                  options_string=options)
                self._v_storage = storage
        elif self.backend == 'bdb':
            storage = getattr(self, '_v_storage', None)
            if storage is None:
                logger.debug("_getGraph: rebuilding bdb storage")
                # XXX AT: check behaviour with multiple access to BDB
                dir_path = os.path.join(CLIENT_HOME, self.bdb_path)
                storage = HashStorage(dir_path, options="hash-type='bdb'")
                self._v_storage = storage
        elif self.backend == 'mysql':
            storage = getattr(self, '_v_storage', None)
            if storage is None:
                logger.debug("_getGraph: rebuilding mysql storage")
                options = self.mysql_options + ",database='%s'"%self.id
                try:
                    storage = Storage(storage_name="mysql",
                                      name=self.id,
                                      options_string=options)
                except Exception, err:
                    # XXX catching RDF.RedlandError is unefficient, because
                    # RedlandError raised in that case does not come from the
                    # Python binding but from C code, even if it has the same
                    # name.
                    if err.__class__.__name__ != 'RedlandError':
                        raise
                    else:
                        # Try to create table: adding the new option creates
                        # tables, but erases data if tables already exist,
                        # that's why it's done after a first try without it.
                        logger.debug("_getGraph: creating mysql tables")
                        options = "new='yes'," + options
                        storage = Storage(storage_name="mysql",
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
    def serialize(self, destination=None,
                  format="application/rdf+xml", base=None):
        """Serialize the graph to destination

        If destination is None then serialization is returned as string.
        """
        rdf_graph = self._getGraph()
        serializer = Serializer(mime_type=format)
        for prefix, uri in self.bindings.items():
            serializer.set_namespace(prefix, uri)
        if destination is None:
            # XXX AT: serializing to string is costly for big graphs ; writing to a
            # file is more efficient
            #res = serializer.serialize_model_to_string(rdf_graph, base_uri=base)
            fd, file_path = tempfile.mkstemp('rdf')
            serializer.serialize_model_to_file(file_path, rdf_graph, base_uri=base)
            os.close(fd)
            f = open(file_path, 'r')
            res = f.read()
            f.flush()
            f.close()
            os.unlink(file_path)
        else:
            res = serializer.serialize_model_to_file(destination, rdf_graph,
                                                     base_uri=base)
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
            triple = (statement.subject,
                      statement.predicate,
                      statement.object)
            items.append(triple)
            related_iter.next()
        return items

    security.declareProtected(View, 'printAllRelations')
    def printAllRelations(self):
        """Print all existing relation instances

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
    def addRelationsFor(self, triples_list):
        """Add given relations to the graph

        triples_list items must be like (uid, relation_id, related_uid)
        Useful when it's costly to access the graph.
        """
        rdf_graph = self._getGraph()
        for subj, pred, obj in triples_list:
            rdf_graph.append(Statement(subj, pred, obj))

    security.declareProtected(View, 'deleteRelationFor')
    def deleteRelationFor(self, uid, relation_id, related_uid):
        """Delete relation for the given object uids and the given relation
        type
        """
        rdf_graph = self._getGraph()
        rdf_graph.remove_statement(Statement(uid, relation_id, related_uid))

    security.declareProtected(View, 'deleteRelationsFor')
    def deleteRelationsFor(self, triples_list):
        """Delete given relations in the graph

        triples_list items must be like (uid, relation_id, related_uid)
        Useful when it's costly to access the graph.

        If related_uid is None, delete all relations found matching the
        statement definition.
        """
        rdf_graph = self._getGraph()
        for subj, pred, obj in triples_list:
            if obj is None:
                self.removeRelationsFor(subj, obj)
            else:
                rdf_graph.remove_statement(Statement(subj, pred, obj))

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
                values.next()
                if not values.end():
                    all_values = [retval] + list(values)
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

    security.declareProtected(View, 'getAllRelationsFor')
    def getAllRelationsFor(self, uid):
        """Get the list of all (predicate, object) tuples for given uid
        """
        rdf_graph = self._getGraph()
        res = []
        # as subject
        related_statement = Statement(uid, None, None)
        related_iter = rdf_graph.find_statements(related_statement)
        while not related_iter.end():
            statement = related_iter.current()
            res.append((statement.predicate, statement.object))
            related_iter.next()
        return res

    security.declareProtected(View, 'getAllInverseRelationsFor')
    def getAllInverseRelationsFor(self, uid):
        """Get the list of all (subject, predicate) tuples for given uid
        """
        rdf_graph = self._getGraph()
        res = []
        # as object
        related_statement = Statement(None, None, uid)
        related_iter = rdf_graph.find_statements(related_statement)
        while not related_iter.end():
            statement = related_iter.current()
            res.append((statement.subject, statement.predicate))
            related_iter.next()
        return res

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

    def getDrawing(self):
        """Get drawing for this graph
        """
        drawer = RedlandGraphDrawer(self)
        ok, res = drawer.getDrawing()
        return ok, res

    #
    # ZMI
    #

    manage_options = (
        {'label': "Relations",
         'action': 'manage_editRelations'
         },
        {'label': "Drawing",
         'action': 'manage_drawing'
         },
        {'label': "Overview",
         'action': 'overview'
         },
        ) + PortalFolder.manage_options[2:]

    security.declareProtected(ManagePortal, 'manage_editRelations')
    manage_editRelations = DTMLFile('zmi/rdfgraph_content', globals())

    security.declareProtected(ManagePortal, 'manage_drawing')
    manage_drawing = DTMLFile('zmi/graph_drawing', globals())

    security.declareProtected(ManagePortal, 'overview')
    overview = DTMLFile('zmi/redlandgraph_overview', globals())

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


class RedlandGraphDrawer(GraphDrawer):

    def _getDotGraph(self):
        """Get the graph in dot language

        Get rela triples, not their string representation
        """
        import pydot
        dot_graph = pydot.Dot(graph_name=self.graph.getId(),
                              type='digraph',
                              simplify=True)
        for triple in self.graph.listAllRelations():
            edge = self._getEdge(triple)
            if edge is not None:
                dot_graph.add_edge(edge)
        return dot_graph

    def _getEdge(self, triple):
        """Get the pydot edge representing the given triple

        Use graph binding to get a clearer drawing
        """
        new_triple = []
        for item in triple:
            if isinstance(item, Node):
                if isinstance(item, unicode):
                    item.encode('utf-8', 'ignore')
                item = str(item)
                if item.startswith('['):
                    item = item[1:]
                if item.endswith(']'):
                    item = item[:-1]
                for key, binding in self.graph.bindings.items():
                    if item.startswith(binding):
                        item = item[len(binding):]
                        item = key + '_' + item
            else:
                if isinstance(item, unicode):
                    item.encode('utf-8', 'ignore')
                item = str(item)
            # dont break label
            item = string.replace(item, ':', '_')
            new_triple.append(item)
        import pydot
        edge = pydot.Edge(new_triple[0], new_triple[2], label=new_triple[1])
        return edge


InitializeClass(RedlandGraphDrawer)
