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
"""CPS Relation Init
"""

import logging

from Products.GenericSetup import profile_registry
from Products.GenericSetup import EXTENSION

from Products.CMFCore.utils import ToolInit
from Products.CMFCore.permissions import AddPortalContent, ManagePortal

from Products.CPSCore.interfaces import ICPSSite

from Products.CPSRelation import relationtool
from Products.CPSRelation import graphregistry

from Products.CPSRelation import objectserializertool
from Products.CPSRelation import objectserializer

from Products.CPSRelation import iobtreegraph
from Products.CPSRelation import iobtreerelation

logger = logging.getLogger("CPSRelation")

USE_RDFLIB = 0
USE_REDLAND = 0

# XXX check that rdflib is installed before importing
try:
    from Products.CPSRelation import rdflibgraph
except ImportError, err:
    msg = "rdflib is not installed (or no compatible version): " \
          "no RDF feature will be available"
    logger.info(msg)
    err_msgs = [
        'No module named rdflib',
        'cannot import name Graph', # rdflib API changes
        ]
    if str(err) not in err_msgs:
        raise
else:
    USE_RDFLIB = 1

# XXX check that Redland is installed before importing
try:
    from Products.CPSRelation import redlandgraph
except ImportError, err:
    msg = "Redland is not installed, no RDF feature will be available"
    logger.info(msg)
    if str(err) != 'No module named RDF':
        raise
else:
    USE_REDLAND = 1

tools = (
    relationtool.RelationTool,
    objectserializertool.ObjectSerializerTool,
    )

def initialize(registrar):
    """Initalization of Relations tool and Relation content
    """
    ToolInit('CPSRelation Tools',
             tools=tools,
             icon='tool.png').initialize(registrar)

    # additional classes, needed for export/import
    registrar.registerClass(
        iobtreegraph.IOBTreeGraph,
        permission=ManagePortal,
        constructors=(relationtool.RelationTool.addGraph,)
        )
    if USE_RDFLIB:
        registrar.registerClass(
            rdflibgraph.RdflibGraph,
            permission=ManagePortal,
            constructors=(relationtool.RelationTool.addGraph,)
            )
    if USE_REDLAND:
        registrar.registerClass(
            redlandgraph.RedlandGraph,
            permission=ManagePortal,
            constructors=(relationtool.RelationTool.addGraph,)
            )
    registrar.registerClass(
        objectserializer.ObjectSerializer,
        permission=ManagePortal,
        constructors=(
        objectserializertool.ObjectSerializerTool.manage_addSerializer,)
        )

    profile_registry.registerProfile(
        'default',
        'CPS Relation',
        "Relation product for CPS.",
        'profiles/default',
        'CPSRelation',
        EXTENSION,
        for_=ICPSSite)
