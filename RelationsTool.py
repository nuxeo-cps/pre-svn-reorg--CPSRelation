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

"""Relation Tool to hold relations between objects

The relations tools stores relation items.
"""

from zLOG import LOG, ERROR, DEBUG, INFO

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.CMFCorePermissions import ManagePortal

from Relation import Relation

class RelationsTool(UniqueObject, PortalFolder):
    """Relations tool

    Relations tool holds Relation objects.
    A Relation object holds a relation table that gives relations between
    objects. It also knows about its inverse Relation table.
    """

    id = 'portal_relations'
    meta_type = 'Relations Tool'

    security = ClassSecurityInfo()

    ###################################################
    # ZMI
    ###################################################

    manage_options = (
        {'label': "Overview",
         'action': 'overview'
         },
        ) + PortalFolder.manage_options

    security.declareProtected(ManagePortal, 'overview')
    overview = DTMLFile('zmi/explainRelationsTool', globals())

    ###################################################
    # RELATIONS TOOL API
    ###################################################

    def __init__(self):
        """Initialization
        """
        PortalFolder.__init__(self, self.id)

    #
    # Relation types management
    #

    security.declarePrivate('_getRelations')
    def _getRelations(self):
        """Get the relations declared in the relations tool
        """
        return self.objectValues('Relation')

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

    security.declarePrivate('_getRelationIds')
    def _getRelationIds(self):
        """Get the relation ids
        """
        return self.objectIds('Relation')

    security.declareProtected(ManagePortal, 'addRelation')
    def addRelation(self, id, inverse_id='', title=''):
        """Add a relation to the relations tool
        """
        if self.hasRelation(id):
            raise ValueError("The id '%s' is invalid - it is already in use"%id)
        else:
            relation = Relation(id=id,
                                title=title,
                                inverse_id=inverse_id,
                                )
            self._setObject(id, relation)

    security.declareProtected(ManagePortal, 'deleteRelation')
    def deleteRelation(self, id):
        """Delete a relation from the relations tool
        """
        if self.hasRelation(id):
            self._delObject(id)

    security.declareProtected(ManagePortal, 'hasRelation')
    def hasRelation(self, id):
        """Does the tool have a relation for the given id?
        """
        relations = self._getRelationIds()
        if id in relations:
            return 1
        else:
            return 0

    #
    # Given relations management
    #

    # XXX Security settings will have to be changed

    security.declarePublic('getRelationFor')
    def getRelationFor(self, uid, relation_id):
        """Get relation for the given object uid and the given relation type
        """
        relation = self._getRelation(relation_id)
        return relation.getRelationFor(uid)

    security.declarePublic('addRelationFor')
    def addRelationFor(self, uid, relation_id, related_uid):
        """Add relation to the given object uid for the given relation type
        """
        relation = self._getRelation(relation_id)
        relation.addRelationFor(uid, related_uid)

    security.declarePublic('removeRelationFor')
    def removeRelationFor(self, uid, relation_id):
        """Remove relation for the given object uid and the given relation type
        """
        relation = self._getRelation(relation_id)
        relation.removeRelationFor(uid)

    security.declarePublic('deleteRelationFor')
    def deleteRelationFor(self, uid, relation_id, related_uid):
        """Delete relation for the given object uids and the given relation
        type
        """
        relation = self._getRelation(relation_id)
        relation.deleteRelationFor(uid, related_uid)

    security.declarePublic('hasRelationFor')
    def hasRelationFor(self, uid, relation_id):
        """Does the relation have a relation for the given object uid and the
        given relation type?
        """
        relations = self.getRelationFor(uid, relation_id)
        if relations:
            return 1
        else:
            return 0

InitializeClass(RelationsTool)
