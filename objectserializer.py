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
"""Object Serializer that provides an expression and a namespace to build an
object serialization
"""

from Globals import InitializeClass
from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager

from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import getEngine

from Products.CPSUtil.PropertiesPostProcessor import PropertiesPostProcessor

class ObjectSerializer(PropertiesPostProcessor, SimpleItemWithProperties):
    """Object Serializer

    Provides an expression and a namespace to build an object serialization
    """

    meta_type = "Object Serializer"

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    _propertiesBaseClass = SimpleItemWithProperties
    _properties = (
        {'id': 'serialization_expr', 'type': 'string', 'mode': 'w',
         'label': 'Serialiation expression'},
        )

    serialization_expr = ''

    _properties_post_process_tales = (
        ('serialization_expr', 'serialization_expr_c'),
        )

    serialization_expr_c = None

    #
    # API
    #

    def __init__(self, id, expression=''):
        """Initialization
        """
        self.id = id
        self.manage_changeProperties(serialization_expr=expression)

    security.declarePrivate('_createSerializationExpressionContext')
    def _createExpressionContext(self, object):
        """Create an expression context for mapping evaluation.
        """
        user = getSecurityManager().getUser()
        portal = getToolByName(self, 'portal_url').getPortalObject()
        rtool = getToolByName(self, 'portal_relations')
        stool = getToolByName(self, 'portal_serializer')
        mapping = {
            'object': object,
            'container': aq_parent(aq_inner(object)),
            'user': user,
            'portal': portal,
            'portal_relations': rtool,
            'portal_serializer': stool,
            }
        graph_types = rtool.getSupportedGraphTypes()
        if 'RDF Graph' in graph_types:
            from rdfgraph import Namespace, RDF, URIRef, Literal
            mapping.update({
                'Namespace': Namespace,
                'RDF': RDF,
                'URIRef': URIRef,
                'Literal': Literal,
                })
        if 'Redland Graph' in graph_types:
            from redlandgraph import Uri, Node, NS
            mapping.update({
                'NS': NS,
                'Uri': Uri,
                'Node': Node,
                })
        return getEngine().getContext(mapping)

    security.declarePrivate('getTriples')
    def getTriples(self, object):
        """Get triples for the given object

        Return a list of triples
        """
        res = None
        if self.serialization_expr_c:
            expr_context = self._createExpressionContext(object)
            res = self.serialization_expr_c(expr_context)
        return res

    #
    # ZMI
    #

    manage_options = SimpleItemWithProperties.manage_options


InitializeClass(ObjectSerializer)

