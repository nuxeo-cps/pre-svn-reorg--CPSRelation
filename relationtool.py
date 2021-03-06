# Copyright (c) 2004-2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# - Anahide Tchertchian <at@nuxeo.com>
# - M.-A. Darche
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
"""Relation tool to manage graphs holding relations between objects.
"""

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from zope.interface import implements

from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.CMFBTreeFolder import CMFBTreeFolder

from Products.CPSRelation.interfaces import IRelationTool
from Products.CPSRelation.graphregistry import GraphRegistry

class RelationTool(UniqueObject, CMFBTreeFolder):
    """Relation tool to manage graphs holding relations between objects.
    """

    id = 'portal_relations'
    meta_type = 'Relation Tool'

    implements(IRelationTool)

    security = ClassSecurityInfo()

    #
    # API
    #

    def __init__(self):
        """Initialization
        """
        CMFBTreeFolder.__init__(self, self.id)

    security.declareProtected(View, 'getSupportedGraphTypes')
    def getSupportedGraphTypes(self):
        """Get supported graph meta types
        """
        return GraphRegistry.listGraphTypes()

    # graphs

    security.declareProtected(ManagePortal, 'listGraphIds')
    def listGraphIds(self):
        """List all the existing graphs
        """
        return CMFBTreeFolder.objectIds_d(self).keys()

    security.declareProtected(ManagePortal, 'deleteAllGraphs')
    def deleteAllGraphs(self):
        """Delete all the graphs.
        """
        for graph_id in self.listGraphIds():
            self.deleteGraph(graph_id)

    security.declareProtected(ManagePortal, 'hasGraph')
    def hasGraph(self, graph_id):
        """Is there a graph with the given id?
        """
        key = CMFBTreeFolder.has_key(self, graph_id)
        if key:
            return 1
        else:
            return 0

    security.declareProtected(ManagePortal, 'addGraph')
    def addGraph(self, graph_id, type, **kw):
        """Add a graph with the given information

        Use a graph registry to instanciate the graph with given type
        """
        if self.hasGraph(graph_id):
            raise KeyError, 'the graph %s already exists.' % graph_id
        graph = GraphRegistry.makeGraph(type, graph_id, **kw)
        return CMFBTreeFolder._setOb(self, graph_id, graph)

    security.declareProtected(ManagePortal, 'deleteGraph')
    def deleteGraph(self, graph_id):
        """Delete graph with given id
        """
        # remove relations in the graph in case it's in a bdb backend
        try:
            graph = self.getGraph(graph_id)
        except KeyError:
            pass
        else:
            graph.deleteAllRelations()
        return CMFBTreeFolder._delOb(self, graph_id)

    security.declareProtected(ManagePortal, 'getGraph')
    def getGraph(self, graph_id):
        """Get the given graph

        Then will be able to query this graph API
        """
        return CMFBTreeFolder._getOb(self, graph_id)

    security.declareProtected(ManagePortal, 'parseGraph')
    def parseGraph(self, graph_id, source, publicID=None, format=None):
        """Parse source into the given graph.

        source can either be a string, location, sml.sax.xmlreader.InputSource
        instance.
        The publicID argument is for specifying the logical URI for the case
        that it's different from the physical source URI.
        """
        graph = self.getGraph(graph_id)
        if format is None:
            res = graph.parse(source, publicID)
        else:
            res = graph.parse(source, publicID, format)
        return res

    security.declareProtected(ManagePortal, 'serializeGraph')
    def serializeGraph(self, graph_id, destination=None,
                       format=None, base=None):
        """Serialize the given graph to destination

        If destination is None then serialization is returned as string.
        """
        graph = self.getGraph(graph_id)
        if format is None:
            res = graph.serialize(destination, base=base)
        else:
            res = graph.serialize(destination, format=format, base=base)
        return res

    # relations

    security.declareProtected(ManagePortal, 'listRelationIds')
    def listRelationIds(self, graph_id):
        """List all the existing relations in the given graph
        """
        graph = self.getGraph(graph_id)
        return graph.listRelationIds()

    security.declareProtected(ManagePortal, 'deleteAllRelations')
    def deleteAllRelations(self, graph_id):
        """Delete all relations in the given graph
        """
        graph = self.getGraph(graph_id)
        return graph.deleteAllRelations()

    security.declareProtected(ManagePortal, 'hasRelation')
    def hasRelation(self, graph_id, relation_id):
        """Does the given graph have a relation with the given id?
        """
        graph = self.getGraph(graph_id)
        return graph.hasRelation(relation_id)

    # XXX AT: see if a relation registry is needed (e.g. add a parameter that
    # gives the relation type)
    security.declareProtected(ManagePortal, 'addRelation')
    def addRelation(self, graph_id, relation_id, **kw):
        """Add a relation with given id to the the given graph
        """
        graph = self.getGraph(graph_id)
        return graph.addRelation(relation_id, **kw)

    security.declareProtected(ManagePortal, 'deleteRelation')
    def deleteRelation(self, graph_id, relation_id):
        """Delete relation with given id from the given graph

        All exiting relation instances for this relation will be deleted
        """
        graph = self.getGraph(graph_id)
        return graph.deleteRelation(relation_id)

    # relation instances

    security.declareProtected(View, 'hasRelationFor')
    def hasRelationFor(self, graph_id, uid, relation_id):
        """Does the given graph have a relation for the given object uid and
        the given relation type?
        """
        graph = self.getGraph(graph_id)
        return graph.hasRelationFor(uid, relation_id)

    security.declareProtected(View, 'addRelationFor')
    def addRelationFor(self, graph_id, uid, relation_id, related_uid):
        """Add relation to the given object uid for the given relation type in
        the given graph
        """
        graph = self.getGraph(graph_id)
        return graph.addRelationFor(uid, relation_id, related_uid)

    security.declareProtected(View, 'addRelationsFor')
    def addRelationsFor(self, graph_id, triples_list):
        """Add given relations to the given graph

        triples_list items must be like (uid, relation_id, related_uid)
        Useful when it's costly to access the graph.
        """
        graph = self.getGraph(graph_id)
        return graph.addRelationsFor(triples_list)

    security.declareProtected(View, 'deleteRelationFor')
    def deleteRelationFor(self, graph_id, uid, relation_id, related_uid):
        """Delete relation for the given object uids and the given relation
        type in the given graph
        """
        graph = self.getGraph(graph_id)
        return graph.deleteRelationFor(uid, relation_id, related_uid)

    security.declareProtected(View, 'deleteRelationsFor')
    def deleteRelationsFor(self, graph_id, triples_list):
        """Delete given relations in the given graph

        triples_list items must be like (uid, relation_id, related_uid)
        Useful when it's costly to access the graph.
        """
        graph = self.getGraph(graph_id)
        return graph.deleteRelationsFor(triples_list)

    security.declareProtected(View, 'getValueFor')
    def getValueFor(self, graph_id, uid, relation_id, related_uid=None,
                    default=None, any=False):
        """Get a value for given uid/relation_id, relation_id/related_uid or
        uid/related_uid pair in the given graph

        Exactly one of uid, relation_id or related_uid must be None.

        default is the value to be returned if no value is found.

        if any is True, return any value if more than one are found. If any is
        False, raise ValueError.
        """
        graph = self.getGraph(graph_id)
        return graph.getValueFor(uid, relation_id, related_uid,
                                 default, any)

    security.declareProtected(View, 'getRelationsFor')
    def getRelationsFor(self, graph_id, uid, relation_id):
        """Get relations for the given object uid and the given relation type
        in the given graph
        """
        graph = self.getGraph(graph_id)
        return graph.getRelationsFor(uid, relation_id)

    security.declareProtected(View, 'getInverseRelationsFor')
    def getInverseRelationsFor(self, graph_id, uid, relation_id):
        """Get relations for the given object uid and the inverse of the given
        relation type in the given graph
        """
        graph = self.getGraph(graph_id)
        return graph.getInverseRelationsFor(uid, relation_id)

    security.declareProtected(View, 'getAllRelationsFor')
    def getAllRelationsFor(self, graph_id, uid):
        """Get the list of all (predicate, object) tuples for given uid in the
        given graph
        """
        graph = self.getGraph(graph_id)
        return graph.getAllRelationsFor(uid)

    security.declareProtected(View, 'getAllInverseRelationsFor')
    def getAllInverseRelationsFor(self, graph_id, uid):
        """Get the list of all (subject, predicate) tuples for given uid in the
        given graph
        """
        graph = self.getGraph(graph_id)
        return graph.getAllInverseRelationsFor(uid)

    security.declareProtected(View, 'removeRelationsFor')
    def removeRelationsFor(self, graph_id, uid, relation_id):
        """Remove relations for the given object uid and the given relation
        type in the given graph
        """
        graph = self.getGraph(graph_id)
        return graph.removeRelationsFor(uid, relation_id)

    security.declareProtected(View, 'removeAllRelationsFor')
    def removeAllRelationsFor(self, graph_id, uid):
        """Remove all relations for the given object uid in the given graph

        This is useful when deleting an object, for instance.
        """
        graph = self.getGraph(graph_id)
        return graph.removeAllRelationsFor(uid)

    def queryGraph(self, graph_id, query_string, **kw):
        """Query the given grah

        Specific arguments can be passed to the graph query method (like
        language used, bindings to apply...
        """
        graph = self.getGraph(graph_id)
        return graph.query(query_string, **kw)

    #
    # ZMI
    #

    manage_options = (
        {'label': "Graphs",
         'action': 'manage_editGraphs'
         },
        {'label': "Overview",
         'action': 'overview'
         },
        ) + CMFBTreeFolder.manage_options[2:4]

    security.declareProtected(ManagePortal, 'manage_editGraphs')
    manage_editGraphs = DTMLFile('zmi/relationtool_graphs', globals())

    security.declareProtected(ManagePortal, 'overview')
    overview = DTMLFile('zmi/relationtool_overview', globals())

    security.declareProtected(ManagePortal, 'manage_listGraphTypes')
    def manage_listGraphTypes(self):
        """List graph types that can be added TTW"""
        return GraphRegistry.listGraphTypes()

    security.declareProtected(ManagePortal, 'manage_addGraph')
    def manage_addGraph(self, id, type, REQUEST=None):
        """Add a graph TTW"""
        self.addGraph(id, type)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()
                                      + '/manage_editGraphs'
                                      '?manage_tabs_message=Graph Added.')

    security.declareProtected(ManagePortal, 'manage_deleteGraphs')
    def manage_deleteGraphs(self, ids, REQUEST=None):
        """Delete graphs TTW."""
        for id in ids:
            self.deleteGraph(id)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()
                                      + '/manage_editGraphs'
                                      '?manage_tabs_message=Deleted.')

    security.declareProtected(ManagePortal, 'manage_deleteAllGraphs')
    def manage_deleteAllGraphs(self, REQUEST=None):
        """Delete graphs TTW."""
        self.deleteAllGraphs()
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()
                                      + '/manage_editGraphs'
                                      '?manage_tabs_message=Deleted.')

InitializeClass(RelationTool)
