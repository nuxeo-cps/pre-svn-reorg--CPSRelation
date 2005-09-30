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
"""Interface for a tool that deals with different relation graphs
"""

import Interface

class IRelationTool(Interface.Base):
    """Interface for a tool that deals with different relation graphs
    """

    # graphs

    def listGraphIds():
        """List all the existing graphs
        """

    def deleteAllGraphs():
        """Delete all graphs
        """

    def hasGraph(graph_id):
        """Is there a graph with the given id?
        """

    def addGraph(graph_id, graph_type, **kw):
        """Add a graph with the given information
        """

    def deleteGraph(graph_id):
        """Delete graph with given id
        """

    def getGraph(graph_id):
        """Get the given graph

        Then will be able to query this graph API
        """

    def parseGraph(graph_id, source, publicID=None, format="xml"):
        """Parse source into the given graph.

        source can either be a string, location, sml.sax.xmlreader.InputSource
        instance.
        Format defaults to xml (AKA rdf/xml).
        The publicID argument is for specifying the logical URI for the case
        that it's different from the physical source URI.
        """

    def serializeGraph(graph_id, destination=None, format='xml', base=None):
        """Serialize the given graph to destination

        If destination is None then serialization is returned as string.
        """

    # relations

    def listRelationIds(graph_id):
        """List all the existing relations in the given graph
        """

    def deleteAllRelations(graph_id):
        """Delete all relations in the given graph
        """

    def hasRelation(graph_id, relation_id):
        """Does the given graph have a relation with the given id?
        """

    # XXX AT: see if a relation registry is needed (e.g. add a parameter that
    # gives the relation type)
    def addRelation(graph_id, relation_id, **kw):
        """Add a relation with given id to the the given graph
        """

    def deleteRelation(graph_id, relation_id):
        """Delete relation with given id from the given graph

        All exiting relation instances for this relation will be deleted
        """

    # relation instances

    def hasRelationFor(graph_id, uid, relation_id):
        """Does the given graph have a relation for the given object uid and
        the given relation type?
        """

    def addRelationFor(graph_id, uid, relation_id, related_uid):
        """Add relation to the given object uid for the given relation type in
        the given graph
        """

    def addRelationsFor(graph_id, triples_list):
        """Add given relations to the given graph

        triples_list items must be like (uid, relation_id, related_uid)
        Useful when it's costly to access the graph.
        """

    def deleteRelationFor(graph_id, uid, relation_id, related_uid):
        """Delete relation for the given object uids and the given relation
        type in the given graph
        """

    def deleteRelationsFor(graph_id, triples_list):
        """Delete given relations in the given graph

        triples_list items must be like (uid, relation_id, related_uid)
        Useful when it's costly to access the graph.
        """

    def getValueFor(graph_id, uid, relation_id, related_uid=None,
                    default=None, any=False):
        """Get a value for given uid/relation_id, relation_id/related_uid or
        uid/related_uid pair in the given graph

        Exactly one of uid, relation_id or related_uid must be None.

        default is the value to be returned if no value is found.

        if any is True, return any value if more than one are found. If any is
        False, raise ValueError.
        """

    def getRelationsFor(graph_id, uid, relation_id):
        """Get relations for the given object uid and the given relation type
        in the given graph
        """

    def getInverseRelationsFor(graph_id, uid, relation_id):
        """Get relations for the given object uid and the inverse of the given
        relation type in the given graph
        """

    def removeRelationsFor(graph_id, uid, relation_id):
        """Remove relations for the given object uid and the given relation
        type in the given graph
        """

    def removeAllRelationsFor(graph_id, uid):
        """Remove all relations for the given object uid in the given graph

        This is useful when deleting an object, for instance.
        """

    def queryGraph(graph_id, query_string, **kw):
        """Query the given graph

        Specific arguments can be passed to the graph query method (like
        language used, bindings to apply...
        """
