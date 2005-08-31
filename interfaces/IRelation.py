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
"""Interface for labeled relations dealing with instances of items to be
related

Note that some graphs may be already dealing with relations internally (for
instance, RDF graphs do).
"""

import Interface

class IRelation(Interface.Base):
    """Interface for labeled relations dealing with instances of items to be
    related
    """

    def listRelationsFor(uid):
        """List all related uids for given object uid
        """

    def hasRelationFor(uid):
        """Is there a relation for the given object uid?
        """

    def addRelationFor(uid, related_uid):
        """Add a relation between he two given object uids
        """

    def getRelationsFor(uid):
        """Get all the related uids for the given object uid
        """

    def getInverseRelationsFor(uid):
        """Get all the related uids for the given object uid considering the
        inverse relation
        """

    def deleteRelationFor(uid, related_uid):
        """Delete a relation between the two given object uids
        """

    def removeAllRelationsFor(uid):
        """Remove all relations for the given object uid

        This is useful when deleting an object, for instance.
        """
