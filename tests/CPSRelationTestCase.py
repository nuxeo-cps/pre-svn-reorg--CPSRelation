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
from Products.CPSDefault.tests import CPSTestCase

ZopeTestCase.installProduct('CPSRelation')

class CPSRelationInstaller(CPSTestCase.CPSInstaller):
    """CPSRelation tests installer"""

    def addPortal(self, id):
        """Override the Default addPortal method installing a Default CPS Site.

        Will launch the CPSRelation installer external method too.
        """

        # CPS Default Site
        CPSTestCase.CPSInstaller.addPortal(self, id)
        portal = getattr(self.app, id)

        # Install the Messager product family
        cpsrelation_installer = ExternalMethod('cpsrelation_installer',
                                               '',
                                               'CPSRelation.install',
                                               'install')
        portal._setObject('cpsrelation_installer', cpsrelation_installer)
        portal.cpsrelation_installer()


class CPSRelationTestCase(CPSTestCase.CPSTestCase):
    """CPSRelation test case"""

    def afterSetUp(self):
        self.login('manager')
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


    def beforeTearDown(self):
        self.logout()


# setup the portal
CPSTestCase.setupPortal(PortalInstaller=CPSRelationInstaller)
