#!/usr/bin/python
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
"""CPSRelation test case
"""

from Testing import ZopeTestCase
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.Portal import manage_addCMFSite

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('MailHost')
ZopeTestCase.installProduct('CPSRelation')

portal_name = 'portal'

class CPSRelationTestCase(ZopeTestCase.PortalTestCase):
    """CPSRelation test case"""

    def getPortal(self):
        if not hasattr(self.app, portal_name):
            manage_addCMFSite(self.app,
                              portal_name)
        return self.app[portal_name]

    def afterSetUp(self):
        # Set portal
        self.portal = self.getPortal()

        try:
            self.login('manager')
        except AttributeError:
            uf = self.portal.acl_users
            uf._doAddUser('manager', '', ['Manager'], [])
            self.login('manager')

        self._setupCPSRelation()
        self._setupTestRelations()

    def beforeTearDown(self):
        self.logout()

    def _setupCPSRelation(self):
        # Launch the CPSRelation installer
        cpsrelation_installer = ExternalMethod('cpsrelation_installer',
                                               '',
                                               'CPSRelation.install',
                                               'install')
        self.portal._setObject('cpsrelation_installer', cpsrelation_installer)
        self.portal.cpsrelation_installer()

    def _setupTestRelations(self):
        self.rtool = getToolByName(self.portal, 'portal_relations')

        # set relations
        self.rtool.addRelation('hasPart',
                               inverse_id='isPartOf',
                               title='has part')
        self.hasPart = self.rtool._getRelation('hasPart')
        self.rtool.addRelation('isPartOf',
                               inverse_id='hasPart',
                               title='is part of')
        self.isPartOf = self.rtool._getRelation('isPartOf')

        # 1 --hasPart--> 10
        # 2 --hasPart--> 10, 23, 25
        self.rtool.addRelationFor(1, 'hasPart', 10)
        self.rtool.addRelationFor(2, 'hasPart', 10)
        self.rtool.addRelationFor(2, 'hasPart', 23)
        self.rtool.addRelationFor(2, 'hasPart', 25)
