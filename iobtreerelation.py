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
"""Relation that holds relations between objects

A relation holds a IOBTree with object uids as keys and tuples of related
object uids as values. It also stores the id of its inverse relation.
"""

from zLOG import LOG, DEBUG, INFO

from Globals import InitializeClass, DTMLFile
from Acquisition import aq_parent, aq_inner
from AccessControl import ClassSecurityInfo

from BTrees.IOBTree import IOBTree

from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.permissions import ManagePortal

from Products.CPSRelation.interfaces.IRelation import IRelation

class IOBTreeRelation(SimpleItemWithProperties):
    """Relation

    A relation holds a BTree with object uids as keys and tuples of related
    object uids as values. It also stores the id of its inverse relation.
    """

    meta_type = 'IOBTree Relation'

    __implements__ = (IRelation,)

    security = ClassSecurityInfo()

    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w',
         'label': 'Title'},
        {'id': 'inverse_id', 'type': 'string', 'mode': 'w',
         'label': 'Inverse relation id'},
        )

    #
    # API
    #

    def __init__(self, id, inverse_id='', title=''):
        """Initialization
        """
        self.id = id
        self.inverse_id = inverse_id
        self.title = title
        self.relations = IOBTree()

    def __cmp__(self, other):
        """Compare method
        """
        try:
            other_id = other.getId()
        except AttributeError:
            other_id = None
        return cmp(self.getId(), other_id)

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

    security.declarePrivate('_addRelationFor')
    def _addRelationFor(self, uid, related_uid):
        """Add relation for the given object uids

        If a relation is already set for the given uid, the tuple of related
        uids is updated.
        """
        if not isinstance(related_uid, int):
            raise TypeError("Related uid is not an integer")
        else:
            related = list(self._getRelationsFor(uid))
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
        if not isinstance(related_uids, tuple):
            raise TypeError("Related uids is not a tuple")
        else:
            self._removeRelationFor(uid)
            self.relations.insert(uid, related_uids)

    security.declarePrivate('_getRelationsFor')
    def _getRelationsFor(self, uid):
        """Get relation for the given object uid
        """
        return self.relations.get(uid, ())

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
        if not isinstance(related_uid, int):
            raise TypeError("Related uid is not an integer")
        else:
            related = list(self._getRelationsFor(uid))
            if related_uid in related:
                related.remove(related_uid)
            if related:
                self._setRelationFor(uid, tuple(related))
            else:
                self._removeRelationFor(uid)

    security.declarePrivate('listRelations')
    def listRelationsFor(self, uid=None):
        """List all relations.

        If uid is not None, keep only relation for this uid.

        Returns a sequence of (uid, (related_uids)).
        """
        if uid is None:
            all = self.relations.items()
        else:
            uid = int(uid)
            related_uids = self.getRelationsFor(uid)
            if related_uids:
                all = ((uid, related_uids),)
            else:
                all = ()
        return all

    #
    # Public/protected API
    #

    # XXX Security settings will have to be changed

    security.declarePublic('hasRelationFor')
    def hasRelationFor(self, uid):
        """Does the given object uid have a relation?
        """
        related = self.getRelationsFor(uid)
        if related:
            return 1
        else:
            return 0

    security.declarePublic('addRelationFor')
    def addRelationFor(self, uid, related_uid):
        """Add relation for the given object uids and update the inverse
        relation
        """
        self._addRelationFor(uid, related_uid)
        inverse_relation = self._getInverseRelation()
        inverse_relation._addRelationFor(related_uid, uid)

    security.declarePublic('getRelationsFor')
    def getRelationsFor(self, uid):
        """Get relation for the given object uid
        """
        res = self._getRelationsFor(uid)
        return res

    security.declarePublic('getInverseRelationsFor')
    def getInverseRelationsFor(self, uid):
        """Get relation for the given object uid
        """
        inverse_relation = self._getInverseRelation()
        res = inverse_relation.getRelationsFor(uid)
        return res

    security.declarePublic('deleteRelationFor')
    def deleteRelationFor(self, uid, related_uid):
        """Delete relation for the given object uids and update the inverse
        relation
        """
        self._deleteRelationFor(uid, related_uid)
        inverse_relation = self._getInverseRelation()
        inverse_relation._deleteRelationFor(related_uid, uid)

    security.declarePublic('removeAllRelationsFor')
    def removeAllRelationsFor(self, uid):
        """Remove relation for the given object uid and update the inverse
        relation
        """
        related = self._getRelationsFor(uid)
        self._removeRelationFor(uid)
        inverse_relation = self._getInverseRelation()
        for related_uid in related:
            inverse_relation._deleteRelationFor(related_uid, uid)

    #
    # ZMI
    #

    manage_options = (SimpleItemWithProperties.manage_options[0],) + (
        {'label': "Contents",
         'action': 'contents'
         },
        {'label': "Overview",
         'action': 'overview'
         },
        ) + SimpleItemWithProperties.manage_options[1:]

    security.declareProtected(ManagePortal, 'contents')
    contents = DTMLFile('zmi/iobtreerelation_content', globals())

    security.declareProtected(ManagePortal, 'overview')
    overview = DTMLFile('zmi/iobtreerelation_overview', globals())

    security.declareProtected(ManagePortal, 'manage_delRelationsFor')
    def manage_addRelationFor(self, uid, related_uid, REQUEST=None):
        """Add relation TTW."""
        self.addRelationFor(uid, related_uid)
        if REQUEST:
            REQUEST.RESPONSE.redirect(
                self.absolute_url()+'/contents'
                '?manage_tabs_message=Added.')

    security.declareProtected(ManagePortal, 'manage_delRelationsFor')
    def manage_delRelationsFor(self, uids, REQUEST=None):
        """Delete relations for given uid TTW."""
        for uid in uids:
            self.removeAllRelationsFor(uid)
        if REQUEST:
            REQUEST.RESPONSE.redirect(
                self.absolute_url()+'/contents'
                '?manage_tabs_message=Deleted.')

InitializeClass(IOBTreeRelation)
