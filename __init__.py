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

""" CPS Relation Init
"""

from Products.CMFCore.utils import ToolInit
from Products.CMFCore.permissions import AddPortalContent

import RelationsTool
import Relation

def initialize(registrar):
    """Initalization of Relations tool and Relation content
    """
    ToolInit(
        'Relations Tool',
        tools=(RelationsTool.RelationsTool,),
        product_name='CPSRelation',
        icon='tool.png'
    ).initialize(registrar)
    registrar.registerClass(
        Relation.Relation,
        permission=AddPortalContent,
        constructors=(
            RelationsTool.RelationsTool.manage_addRelation,
            )
        )
