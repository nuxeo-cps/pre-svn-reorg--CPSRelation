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
"""Graph using IOBtree objects to store relations between integers
"""

from zLOG import LOG, ERROR, DEBUG, INFO

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.PortalFolder import PortalFolder

from Products.CPSRelation.interfaces.IGraph import IGraph
from Products.CPSRelation.iobtreerelation import IOBTreeRelation
from Products.CPSRelation.graphregistry import GraphRegistry
from Products.CPSRelation.graphdrawer import GraphDrawer

class IOBTreeGraph(UniqueObject, PortalFolder):
    """Graph using IOBtree objects to store relations between integers
    """

    meta_type = 'IOBTree Graph'

    __implements__ = (IGraph,)

    security = ClassSecurityInfo()

    #
    # API
    #

    def __init__(self, id, **kw):
        """Initialization
        """
        PortalFolder.__init__(self, id, **kw)

    #
    # Relation types management
    #

    security.declarePrivate('_getRelations')
    def _getRelations(self):
        """Get the relations declared in the relations tool
        """
        return self.objectValues()

    security.declarePrivate('_getRelation')
    def _getRelation(self, id):
        """Get a relation held in the relations tool.
        """
        try:
            relation = self._getOb(id)
        except AttributeError:
            raise AttributeError("Relation '%s' does not exist" %id)
        else:
            return relation

    security.declareProtected(ManagePortal, 'parse')
    def parse(self, source, publicID=None, format="xml"):
        """Parse source into Graph.

        source can either be a string, location, sml.sax.xmlreader.InputSource
        instance.
        Format defaults to xml (AKA rdf/xml).
        The publicID argument is for specifying the logical URI for the case
        that it's different from the physical source URI.
        """
        raise NotImplementedError

    security.declareProtected(ManagePortal, 'serialize')
    def serialize(self, destination=None, format='xml', base=None):
        """Serialize the graph to destination

        If destination is None then serialization is returned as string.
        """
        raise NotImplementedError

    security.declareProtected(ManagePortal, 'listRelationIds')
    def listRelationIds(self):
        """Get the relation ids
        """
        return self.objectIds()

    security.declareProtected(ManagePortal, 'deleteAllRelations')
    def deleteAllRelations(self):
        """Delete all relations.
        """
        for id in self.listRelationIds():
            self.deleteRelation(id)

    security.declareProtected(ManagePortal, 'hasRelation')
    def hasRelation(self, id):
        """Does the tool have a relation for the given id?
        """
        relations = self.listRelationIds()
        if id in relations:
            return 1
        else:
            return 0

    security.declareProtected(ManagePortal, 'addRelation')
    def addRelation(self, id, inverse_id='', title='', **kw):
        """Add a relation to the relations tool
        """
        if self.hasRelation(id):
            raise ValueError("The id '%s' is invalid - it is already in use"%id)
        else:
            relation = IOBTreeRelation(id=id,
                                       title=title,
                                       inverse_id=inverse_id)
            self._setObject(id, relation)
            return self._getOb(id)

    security.declareProtected(ManagePortal, 'deleteRelation')
    def deleteRelation(self, id):
        """Delete a relation from the relations tool
        """
        if self.hasRelation(id):
            self._delObject(id)

    #
    # relation instances
    #

    security.declareProtected(View, 'listAllRelations')
    def listAllRelations(self):
        """List all relation instances, return triples
        """
        res = []
        for rel_id in self.listRelationIds():
            relation = self._getRelation(rel_id)
            all_relations = relation.listRelationsFor()
            # all_relations is a list of items (uid, tuple of related uids)
            new_relations = []
            for related in all_relations:
                uid = related[0]
                for related_uid in related[1]:
                    new_relations.append((uid, rel_id, related_uid))
            res.extend(new_relations)
        return res

    security.declareProtected(View, 'printAllRelations')
    def printAllRelations(self):
        """print all relation instances, return string triples
        """
        res = []
        for rel_id in self.listRelationIds():
            relation = self._getRelation(rel_id)
            all_relations = relation.listRelationsFor()
            # all_relations is a list of items (uid, tuple of related uids)
            new_relations = []
            for related in all_relations:
                uid = related[0]
                for related_uid in related[1]:
                    new_relations.append((str(uid), rel_id, str(related_uid)))
            res.extend(new_relations)
        return res

    security.declareProtected(View, 'hasRelationFor')
    def hasRelationFor(self, uid, relation_id):
        """Does the relation have a relation for the given object uid and the
        given relation type?
        """
        relations = self.getRelationsFor(uid, relation_id)
        if relations:
            return 1
        else:
            return 0

    security.declareProtected(View, 'addRelationFor')
    def addRelationFor(self, uid, relation_id, related_uid):
        """Add relation to the given object uid for the given relation type
        """
        relation = self._getRelation(relation_id)
        relation.addRelationFor(uid, related_uid)

    security.declareProtected(View, 'addRelationsFor')
    def addRelationsFor(self, triples_list):
        """Add given relations to the graph

        triples_list items must be like (uid, relation_id, related_uid)
        Useful when it's costly to access the graph.
        """
        # sort by relation_id
        relations_sorted = {}
        for item in triples_list:
            relation_id = item[1]
            if relation_id not in relations_sorted:
                relations_sorted[relation_id] = [item]
            else:
                new_value = relations_sorted[relation_id]
                new_value.append(item)
                relations_sorted[relation_id] = new_value
        for relation_id, triples in relations_sorted.items():
            relation = self._getRelation(relation_id)
            for item in triples:
                relation.addRelationFor(item[0], item[2])

    security.declareProtected(View, 'deleteRelationFor')
    def deleteRelationFor(self, uid, relation_id, related_uid):
        """Delete relation for the given object uids and the given relation
        type
        """
        relation = self._getRelation(relation_id)
        relation.deleteRelationFor(uid, related_uid)

    security.declareProtected(View, 'deleteRelationsFor')
    def deleteRelationsFor(self, triples_list):
        """Delete given relations in the graph

        triples_list items must be like (uid, relation_id, related_uid)
        Useful when it's costly to access the graph.
        """
        # sort by relation_id
        # sort by relation_id
        relations_sorted = {}
        for item in triples_list:
            relation_id = item[1]
            if relation_id not in relations_sorted:
                relations_sorted[relation_id] = [item]
            else:
                new_value = relations_sorted[relation_id]
                new_value.append(item)
                relations_sorted[relation_id] = new_value
        for relation_id, triples in relations_sorted.items():
            relation = self._getRelation(relation_id)
            for item in triples:
                relation.deleteRelationFor(item[0], item[2])

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
        if related_uid is None:
            assert uid is not None
            assert relation_id is not None
            values = self.getRelationsFor(uid, relation_id)
        if uid is None:
            assert relation_id is not None
            assert related_uid is not None
            values = self.getInverseRelationsFor(related_uid, relation_id)
        if relation_id is None:
            assert uid is not None
            assert related_uid is not None
            # XXX no implementation for this kind of query in btrees for now
            raise NotImplementedError

        retval = default
        if len(values) > 1 and any is False:
            raise ValueError(values)
        elif values:
            retval = values[0]

        return retval

    security.declareProtected(View, 'getRelationsFor')
    def getRelationsFor(self, uid, relation_id):
        """Get relation for the given object uid and the given relation type
        """
        relation = self._getRelation(relation_id)
        return relation.getRelationsFor(uid)

    security.declareProtected(View, 'getInverseRelationsFor')
    def getInverseRelationsFor(self, uid, relation_id):
        """Get relation for the given object uid and the given relation type
        """
        relation = self._getRelation(relation_id)
        inverse_relation = relation._getInverseRelation()
        return inverse_relation.getRelationsFor(uid)

    security.declareProtected(View, 'getAllRelationsFor')
    def getAllRelationsFor(self, uid):
        """Get the list of all (predicate, object) tuples for given uid
        """
        res = []
        relations = self._getRelations()
        for relation in relations:
            related = relation.getRelationsFor(uid)
            relation_id = relation.getId()
            tuples = [(relation_id, x) for x in related]
            res.extend(tuples)
        return res

    security.declareProtected(View, 'getAllInverseRelationsFor')
    def getAllInverseRelationsFor(self, uid):
        """Get the list of all (subject, predicate) tuples for given uid
        """
        res = []
        relations = self._getRelations()
        for relation in relations:
            related = relation.getInverseRelationsFor(uid)
            relation_id = relation.getId()
            tuples = [(x, relation_id) for x in related]
            res.extend(tuples)
        return res

    security.declareProtected(View, 'removeRelationsFor')
    def removeRelationsFor(self, uid, relation_id):
        """Remove relation for the given object uid and the given relation type
        """
        relation = self._getRelation(relation_id)
        relation.removeAllRelationsFor(uid)

    security.declareProtected(View, 'removeAllRelationsFor')
    def removeAllRelationsFor(self, uid):
        """Remove all relations for the given object uid

        This is useful when deleting an object, for instance.
        """
        relations = self._getRelations()
        for relation in relations:
            relation.removeAllRelationsFor(uid)

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
        ) + PortalFolder.manage_options[3:-2]

    security.declareProtected(ManagePortal, 'manage_editRelations')
    manage_editRelations = DTMLFile('zmi/iobtreegraph_content', globals())

    security.declareProtected(ManagePortal, 'manage_drawing')
    manage_drawing = DTMLFile('zmi/graph_drawing', globals())

    security.declareProtected(ManagePortal, 'overview')
    overview = DTMLFile('zmi/iobtreegraph_overview', globals())

    security.declareProtected(ManagePortal, 'manage_addRelation')
    def manage_addRelation(self, id, inverse_id, title='', REQUEST=None):
        """Add a relation TTW."""
        relation = self.addRelation(id, inverse_id, title)
        if REQUEST:
            REQUEST.RESPONSE.redirect(
                self.absolute_url()+'/manage_editRelations'
                '?manage_tabs_message=Added.')
        else:
            return relation

    security.declareProtected(ManagePortal, 'manage_delRelations')
    def manage_delRelations(self, ids, REQUEST=None):
        """Delete relations TTW."""
        for id in ids:
            self.deleteRelation(id)
        if REQUEST:
            REQUEST.RESPONSE.redirect(
                self.absolute_url()+'/manage_editRelations'
                '?manage_tabs_message=Deleted.')

    security.declareProtected(ManagePortal, 'manage_delAllRelations')
    def manage_delAllRelations(self, REQUEST=None):
        """Delete all relations TTW."""
        self.deleteAllRelations()
        if REQUEST:
            REQUEST.RESPONSE.redirect(
                self.absolute_url()+'/manage_editRelations'
                '?manage_tabs_message=Deleted.')


InitializeClass(IOBTreeGraph)

# Register to the graph registry
GraphRegistry.register(IOBTreeGraph)
