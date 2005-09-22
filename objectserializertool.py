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
"""
Object Serializer Tool that provides services to get RDF serializations of
objects
"""

# XXX Currently requires Serializer from RDF to serialize to RDF/XML files

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.CMFBTreeFolder import CMFBTreeFolder

from Products.CPSRelation.objectserializer import ObjectSerializer

class ObjectSerializerTool(UniqueObject, CMFBTreeFolder):
    """Object Serializer Tool that provides services to get RDF serializations of
    objects

    Stores definitions of mappings between objects and their rdf view (triples)
    """

    id = 'portal_serializer'
    meta_type = "Object Serializer Tool"

    security = ClassSecurityInfo()

    #
    # API
    #

    def __init__(self):
        """Initialization
        """
        CMFBTreeFolder.__init__(self, self.id)

    security.declareProtected(View, 'listSerializers')
    def listSerializers(self):
        """List object serializers managed by the tool
        """
        return CMFBTreeFolder.objectIds_d(self).keys()

    security.declareProtected(View, 'hasSerializer')
    def hasSerializer(self, id):
        """Does the tool have the given object serializer?
        """
        key = CMFBTreeFolder.has_key(self, id)
        if key:
            return 1
        else:
            return 0

    security.declareProtected(ManagePortal, 'addSerializer')
    def addSerializer(self, id, expr='', bindings={}):
        """Add an object serializer with given id and expression
        """
        if self.hasSerializer(id):
            raise ValueError("The id '%s' is invalid - it is already in use"%id)
        else:
            ser = ObjectSerializer(id, expr, bindings)
            self._setObject(id, ser)
            return self._getOb(id)

    security.declareProtected(ManagePortal, 'deleteSerializer')
    def deleteSerializer(self, id):
        """Delete given object serializer
        """
        if self.hasSerializer(id):
            self._delObject(id)

    security.declarePrivate('getSerializer')
    def getSerializer(self, id):
        """Get object serializer with given id
        """
        try:
            ser = self._getOb(id)
        except KeyError:
            raise AttributeError("Serializer '%s' does not exist" %id)
        else:
            return ser

    # serialization operations

    security.declareProtected(View, 'getSerializationTriples')
    def getSerializationTriples(self, object, serializer_id):
        """Get Serialization for given object using given serializer

        return serialization as a list of triples
        """
        ser = self.getSerializer(serializer_id)
        triples = ser.getTriples(object)
        return triples

    # XXX AT: Currently requires Redland
    security.declarePrivate('serializeTriples')
    def serializeTriples(self, triples, base=None, bindings={}):
        """Serialize triples to an rdf/xml string using the optional base URI
        """
        from Products.CPSRelation.redlandgraph import Model, Statement
        from Products.CPSRelation.redlandgraph import Storage, Serializer
        # create an rdf_graph with a memory storage for given purpose
        options = "new='yes',hash-type='memory',dir='.'"
        storage = Storage(storage_name="hashes",
                          name='dummy',
                          options_string=options)
        rdf_graph = Model(storage)
        for item in triples:
            rdf_graph.append(Statement(item[0], item[1], item[2]))
        serializer = Serializer(mime_type="application/rdf+xml")
        for prefix, uri in bindings.items():
            serializer.set_namespace(prefix, uri)
        res = serializer.serialize_model_to_string(rdf_graph, base_uri=base)
        return res

    # XXX AT: Currently requires Redland
    security.declareProtected(View, 'getSerialization')
    def getSerialization(self, object, serializer_id, base=None):
        """Get Serialization for given object using given serializer

        Serialize found triples to an rdf/xml string using the optional base
        URI
        """
        ser = self.getSerializer(serializer_id)
        triples = ser.getTriples(object)
        bindings = ser.getBindings()
        return self.serializeTriples(triples, base=base, bindings=bindings)

    # XXX AT: Currently requires Redland
    security.declareProtected(View, 'getSerialization')
    def getMultipleSerialization(self, objects_info, base=None):
        """Get Serialization for given objects

        objects_info is a sequence of items with object as first element and
        serializer id as second element.

        Serialize found triples to an rdf/xml string using the optional base
        URI
        """
        all_triples = []
        all_bindings = {}
        for object_info in objects_info:
            ser = self.getSerializer(object_info[1])
            triples = ser.getTriples(object_info[0])
            all_triples.extend(triples)
            all_bindings.update(ser.getBindings())
        return self.serializeTriples(all_triples, base=base,
                                     bindings=all_bindings)

    #
    # ZMI
    #

    # Here define options using DTML files
    manage_options = (
        {'label': "Object Serializers",
         'action': 'manage_main'
         },
        # XXX AT: doc is not ready yet
        #{'label': "Overview",
        # 'action': 'overview'
        # },
        ) + CMFBTreeFolder.manage_options[2:4]

    security.declareProtected(ManagePortal, 'manage_main')
    manage_main = DTMLFile('zmi/objectserializertool_content', globals())

    security.declareProtected(ManagePortal, 'overview')
    overview = DTMLFile('zmi/objectserializertool_overview', globals())

    security.declareProtected(ManagePortal, 'manage_addSerializer')
    def manage_addSerializer(self, id, serialization_expr, bindings,
                             REQUEST=None):
        """Add a graph TTW"""
        self.addSerializer(id, serialization_expr, bindings)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main'
                                      '?manage_tabs_message=Serializer Added.')

    security.declareProtected(ManagePortal, 'manage_editSerializers')
    def manage_editSerializers(self,
                               all_ids,
                               serialization_expressions,
                               all_bindings,
                               REQUEST=None,
                               ):
        """Edit Object Serializers TTW.
        """
        for index, id in enumerate(all_ids):
            if self.hasSerializer(id):
                expr = serialization_expressions[index]
                bindings = all_bindings[index]
                kw = {
                    'serialization_expr': expr,
                    'bindings': bindings,
                    }
                serializer = self.getSerializer(id)
                serializer.manage_changeProperties(**kw)
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main'
                                      '?manage_tabs_message=Edited.')

    security.declareProtected(ManagePortal, 'manage_deleteSerializers')
    def manage_deleteSerializers(self, checked_ids, REQUEST=None):
        """Delete object serializers TTW."""
        for id in checked_ids:
            self.deleteSerializer(id)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main'
                                      '?manage_tabs_message=Deleted.')

    security.declareProtected(ManagePortal, 'manage_deleteAllSerializers')
    def manage_deleteAllSerializers(self, REQUEST=None):
        """Delete all object serializers TTW."""
        for id in self.listSerializers():
            self.deleteSerializer(id)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main'
                                      '?manage_tabs_message=Deleted.')



InitializeClass(ObjectSerializerTool)

