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
#-------------------------------------------------------------------------------
# $Id$
#-------------------------------------------------------------------------------
"""Object Serializer that provides an expression and a namespace to build an
object serialization
"""

from Globals import InitializeClass
from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager

from zope.interface import implements

from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import getEngine

from Products.CPSUtil.PropertiesPostProcessor import PropertiesPostProcessor

from Products.CPSRelation.interfaces import IObjectSerializer

class ObjectSerializer(PropertiesPostProcessor, SimpleItemWithProperties):
    """Object Serializer

    Provides an expression and a namespace to build an object serialization
    """

    meta_type = "Object Serializer"

    implements(IObjectSerializer)

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    _propertiesBaseClass = SimpleItemWithProperties
    _properties = (
        {'id': 'serialization_expr', 'type': 'string', 'mode': 'w',
         'label': 'Serialization expression'},
        # one binding per line, following the format "key value", for instance:
        # rdf http://www.w3.org/1999/02/22-rdf-syntax-ns#
        # exp http://www.example.org/
        {'id': 'bindings', 'type': 'lines', 'mode': 'w',
         'label': 'Prefix/Uri bindings'},
        )

    serialization_expr = ''
    bindings = ()

    _properties_post_process_tales = (
        ('serialization_expr', 'serialization_expr_c'),
        )

    serialization_expr_c = None

    #
    # API
    #

    def __init__(self, id, expression='', bindings=()):
        """Initialization
        """
        self.id = id
        self.manage_changeProperties(serialization_expr=expression,
                                     bindings=bindings)

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
            'proxy': object,
            'container': aq_parent(aq_inner(object)),
            'user': user,
            'portal': portal,
            'portal_relations': rtool,
            'portal_serializer': stool,
            }
        graph_types = rtool.getSupportedGraphTypes()
        if 'Rdflib Graph' in graph_types:
            from rdflibgraph import Namespace, RDF, URIRef, Literal
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

    def getBindings(self):
        """Get defined bindings dictionnary
        """
        bindings_dict = {}
        for binding in self.bindings:
            sep_index = binding.find(' ')
            if sep_index != -1:
                key = binding[:sep_index]
                value = binding[sep_index+1:]
                bindings_dict[key] = value
        return bindings_dict

    #
    # ZMI
    #

    manage_options = SimpleItemWithProperties.manage_options


InitializeClass(ObjectSerializer)
