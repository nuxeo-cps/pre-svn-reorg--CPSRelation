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

"""Relation that holds relations between objects

A relation holds a BTree with object uids as keys and tuples of related object
uids as values. It also stores the id of its inverse relation.
"""

from zLOG import LOG, DEBUG, INFO

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_inner

from types import IntType, TupleType
from BTrees.IOBTree import IOBTree
from Products.CMFCore.utils import SimpleItemWithProperties

from Products.CMFCore.CMFCorePermissions import ManagePortal

class Relation(SimpleItemWithProperties):
    """Relation

    A relation holds a BTree with object uids as keys and tuples of related object
    uids as values. It also stores the id of its inverse relation.
    """

    meta_type = 'Relation'

    security = ClassSecurityInfo()

    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w',
         'label': 'Title'},
        {'id': 'inverse_id', 'type': 'string', 'mode': 'w',
         'label': 'Inverse relation id'},
        )

    ###################################################
    # ZMI
    ###################################################

    manage_options = SimpleItemWithProperties.manage_options + (
        {'label': "Overview",
         'action': 'overview'
         },
        )

    security.declareProtected(ManagePortal, 'overview')
    overview = DTMLFile('zmi/explainRelation', globals())

    ###################################################
    # RELATIONS TOOL API
    ###################################################

    def __init__(self, id, inverse_id, title=''):
        """Initialization
        """
        self.id = id
        self.inverse_id = inverse_id
        self.title = title
        self.relations = IOBTree()

    #
    # Private API
    #

    security.declarePrivate('_getInverseRelationId')
    def _getInverseRelationId(self):
        """Get the inverse relation id
        """
        if not self.inverse_id:
            raise ValueError("Inverse relation id is required")
        else:
            return self.inverse_id

    security.declarePrivate('_getInverseRelation')
    def _getInverseRelation(self):
        """Get the inverse relation
        """
        inverse_id = self._getInverseRelationId()
        container = aq_parent(aq_inner(self))
        try:
            inverse_rel = container._getOb(inverse_id)
        except AttributeError:
            raise AttributeError("Inverse relation '%s' does not exist" %
                                 inverse_id)
        else:
            return inverse_rel

    security.declarePrivate('_getRelationFor')
    def _getRelationFor(self, uid):
        """Get relation for the given object uid
        """
        return self.relations.get(uid, ())

    security.declarePrivate('_addRelationFor')
    def _addRelationFor(self, uid, related_uid):
        """Add relation for the given object uids

        If a relation is already set for the given uid, the tuple of related
        uids is updated.
        """
        if not isinstance(related_uid, IntType):
            raise TypeError("Related uid is not an integer")
        else:
            related = list(self._getRelationFor(uid))
            if related_uid not in related:
                related.append(related_uid)
            if related:
                self._setRelationFor(uid, tuple(related))
            else:
                self._removeRelationFor(uid)

    security.declarePrivate('_setRelationFor')
    def _setRelationFor(self, uid, related_uids):
        """Set relation for the given object uid

        The related uids is a tuple of object uids.
        """
        if not isinstance(related_uids, TupleType):
            raise TypeError("Related uids is not a tuple")
        else:
            self._removeRelationFor(uid)
            self.relations.insert(uid, related_uids)

    security.declarePrivate('_removeRelationFor')
    def _removeRelationFor(self, uid):
        """Remove relation for the given object uid
        """
        if self.relations.has_key(uid):
            del self.relations[uid]

    security.declarePrivate('_deleteRelationFor')
    def _deleteRelationFor(self, uid, related_uid):
        """Delete the relation for the given object uids
        """
        if not isinstance(related_uid, IntType):
            raise TypeError("Related uid is not an integer")
        else:
            related = list(self._getRelationFor(uid))
            if related_uid in related:
                related.remove(related_uid)
            if related:
                self._setRelationFor(uid, tuple(related))
            else:
                self._removeRelationFor(uid)


    #
    # Public/protected API
    #

    # XXX Security settings will have to be changed

    security.declarePublic('getRelationFor')
    def getRelationFor(self, uid):
        """Get relation for the given object uid
        """
        return self._getRelationFor(uid)

    security.declarePublic('addRelationFor')
    def addRelationFor(self, uid, related_uid):
        """Add relation for the given object uids and update the inverse
        relation
        """
        self._addRelationFor(uid, related_uid)
        inverse_relation = self._getInverseRelation()
        inverse_relation._addRelationFor(related_uid, uid)

    security.declarePublic('removeRelationFor')
    def removeRelationFor(self, uid):
        """Remove relation for the given object uid and update the inverse
        relation
        """
        related = self._getRelationFor(uid)
        self._removeRelationFor(uid)
        inverse_relation = self._getInverseRelation()
        for related_uid in related:
            inverse_relation._deleteRelationFor(related_uid, uid)

    security.declarePublic('deleteRelationFor')
    def deleteRelationFor(self, uid, related_uid):
        """Delete relation for the given object uids and update the inverse
        relation
        """
        self._deleteRelationFor(uid, related_uid)
        inverse_relation = self._getInverseRelation()
        inverse_relation._deleteRelationFor(related_uid, uid)

    security.declarePublic('hasRelationFor')
    def hasRelationFor(self, uid):
        """Does the given object uid have a relation?
        """
        related = self.getRelationFor(uid)
        if related:
            return 1
        else:
            return 0

InitializeClass(Relation)
