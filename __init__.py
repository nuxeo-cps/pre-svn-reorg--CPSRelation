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
# $Id$

""" CPS Relation Init
"""

from zLOG import LOG, INFO

from Products.CMFCore.utils import ToolInit
from Products.CMFCore.permissions import AddPortalContent

from Products.CPSRelation import relationtool
from Products.CPSRelation import graphregistry

from Products.CPSRelation import iobtreegraph
from Products.CPSRelation import iobtreerelation

# XXX check that rdflib is installed before importing
try:
    from Products.CPSRelation import rdfgraph
except ImportError, err:
    LOG("CPSRelation", INFO,
        "rdflib is not installed, no RDF feature will be available")
    print "WARNING: rdflib is not installed, no RDF feature will be available"
    if str(err) != 'No module named rdflib':
        raise

def initialize(registrar):
    """Initalization of Relations tool and Relation content
    """
    ToolInit(
        'Relation Tool',
        tools=(relationtool.RelationTool,),
        icon='tool.png'
        ).initialize(registrar)

    #registrar.registerClass(
    #    relationtool.RelationTool,
    #    permission='AddPortalContent',
    #    constructors=(
    #    RelationTool.manage_addRelationTool,
    #    #RelationTool.manage_addRelationToolForm,
    #    ),
    #    )
    #
    #registrar.registerClass(
    #    Relation.Relation,
    #    permission=AddPortalContent,
    #    constructors=(
    #        RelationTool.RelationTool.manage_addRelation,
    #        )
    #    )
