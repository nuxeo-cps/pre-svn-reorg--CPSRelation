# Copyright (c) 2005 Nuxeo SARL <http://nuxeo.com>
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
# $Id$
"""Interface for graphs dealing with several labeled relations
"""

import Interface

class IGraph(Interface.Base):
    """Interface for graphs dealing with several labeled relations
    """

    # I/O

    def parse(source, publicID=None, format="xml"):
        """Parse source into the graph.

        source can either be a string, location, sml.sax.xmlreader.InputSource
        instance.
        Format defaults to xml (AKA rdf/xml).
        The publicID argument is for specifying the logical URI for the case
        that it's different from the physical source URI.
        """

    def serialize(destination=None, format='xml', base=None):
        """Serialize the graph to destination

        If destination is None then serialization is returned as string.
        """

    # relations

    def listRelationIds():
        """List all the existing relations.
        """

    def deleteAllRelations():
        """Delete all relations.
        """

    def hasRelation(relation_id):
        """Does the graph have a relation with the given id?
        """

    # XXX AT: see if a relation registry is needed (e.g. add a parameter that
    # gives the relation type)
    def addRelation(relation_id, **kw):
        """Add a relation with given id to the graph
        """
    def deleteRelation(relation_id):
        """Delete relation with given id from the graph

        All exiting relation instances for this relation will be deleted
        """

    # relation instances

    def listAllRelations():
        """List all relation instances
        """

    def hasRelationFor(uid, relation_id):
        """Does the graph have a relation for the given object uid and the
        given relation type?
        """

    def addRelationFor(uid, relation_id, related_uid):
        """Add relation to the given object uid for the given relation type
        """

    def addRelationsFor(triplets_list):
        """Add given relations to the graph

        triplets_list items must be like (uid, relation_id, related_uid)
        Useful when it's costly to access the graph.
        """

    def deleteRelationFor(uid, relation_id, related_uid):
        """Delete relation for the given object uids and the given relation
        type
        """

    def deleteRelationsFor(triplets_list):
        """Delete given relations in the graph

        triplets_list items must be like (uid, relation_id, related_uid)
        Useful when it's costly to access the graph.
        """

    def getValueFor(uid, relation_id, related_uid=None,
                    default=None, any=False):
        """Get a value for given uid/relation_id, relation_id/related_uid or
        uid/related_uid pair.

        Exactly one of uid, relation_id or related_uid must be None.

        default is the value to be returned if no value is found.

        if any is True, return any value if more than one are found. If any is
        False, raise ValueError.
        """

    def getRelationsFor(uid, relation_id):
        """Get relations for the given object uid and the given relation type
        """

    def getInverseRelationsFor(uid, relation_id):
        """Get relations for the given object uid and the inverse of the given
        relation type
        """

    def removeRelationsFor(uid, relation_id):
        """Remove relations for the given object uid and the given relation
        type
        """

    def removeAllRelationsFor(uid):
        """Remove all relations for the given object uid

        This is useful when deleting an object, for instance.
        """

    def query(query_string, **kw):
        """Query the graph

        Specific arguments can be passed to the graph query method (like
        language used, bindings to apply...
        """
