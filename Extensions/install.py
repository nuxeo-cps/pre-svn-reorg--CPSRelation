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
"""
CPSRelation Installer

Howto use the CPSRelation installer :
 - Log into the ZMI as manager
 - Go to your CPS root directory
 - Create an External Method with the following parameters:

     id            : cpsrelation_install (or whatever)
     title         : CPSRelation Install (or whatever)
     Module Name   : CPSRelation.install
     Function Name : install

 - save it
 - then click on the test tab of this external method
"""

from zLOG import LOG, INFO, DEBUG

from Products.CPSInstaller.CPSInstaller import CPSInstaller
from Products.CMFCore.utils import getToolByName

class CPSRelationInstaller(CPSInstaller):

    def install(self):
        self.log("### Starting CPSRelation install ###")
        self.setupRelationsTool()
        self.log("### End of specific CPSRelation install ###")

    def setupRelationsTool(self):
        self.log("Checking Relations Tool")
        self.verifyTool('portal_relations',
                        'CPSRelation',
                        'Relations Tool')


def install(self):
    installer = CPSRelationInstaller(self, 'CPSRelation')
    installer.install()
    return installer.logResult()
