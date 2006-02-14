# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
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
"""CPSRelation XML Adapters.
"""

from zope.component import adapts
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron

from Products.CPSRelation.interfaces import IRelationTool
from Products.CPSRelation.interfaces import IGraph
from Products.CPSRelation.interfaces import IRelation
from Products.CPSRelation.interfaces import IObjectSerializerTool
from Products.CPSRelation.interfaces import IObjectSerializer

REL_TOOL = 'portal_relations'
REL_NAME = 'graphs'

SER_TOOL = 'portal_serializer'
SER_NAME = 'serializers'

# relations

def exportRelationTool(context):
    """Export relations tool and IOBTreeRelation objects as a set of XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, REL_TOOL, None)
    if tool is None:
        logger = context.getLogger(REL_NAME)
        logger.info("Nothing to export.")
        return
    exportObjects(tool, '', context)


def importRelationTool(context):
    """Import relations tool and IOBTreeRelation objects from a set of XML
    files.
    """
    site = context.getSite()
    tool = getToolByName(site, REL_TOOL)
    importObjects(tool, '', context)


class RelationToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers):
    """XML importer and exporter for Relation tool.
    """
    adapts(IRelationTool, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = REL_NAME
    name = REL_NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractObjects())
        self._logger.info("Relation tool exported.")
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeObjects()
        self._initObjects(node)
        self._logger.info("Relation tool imported.")

# XXX need to create relations for IOBTree graphs when importing... (relations
# are somehow exported (?))
class GraphXMLAdapter(XMLAdapterBase, PropertyManagerHelpers,
                      ObjectManagerHelpers):
    """XML importer and exporter for a graph.
    """
    adapts(IGraph, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = REL_NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        self._logger.info("%s graph exported." % self.context.getId())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
        self._initProperties(node)
        self._logger.info("%s graph imported." % self.context.getId())


class RelationXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """XML importer and exporter for a relation of an IOBTree graph.
    """
    adapts(IRelation, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = REL_NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        self._logger.info("%s relation exported." % self.context.getId())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
        self._initProperties(node)
        self._logger.info("%s relation imported." % self.context.getId())


# object serializer

def exportObjectSerializerTool(context):
    """Export ObjectSerializer tool and serializers as a set of XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, SER_TOOL, None)
    if tool is None:
        logger = context.getLogger(SER_NAME)
        logger.info("Nothing to export.")
        return
    exportObjects(tool, '', context)

def importObjectSerializerTool(context):
    """Import tool and serializers from a set of XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, SER_TOOL)
    importObjects(tool, '', context)


class ObjectSerializerToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers):
    """XML importer and exporter for ObjectSerializer tool.
    """
    adapts(IObjectSerializerTool, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = SER_NAME
    name = SER_NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractObjects())
        self._logger.info("ObjectSerializer tool exported.")
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeObjects()
        self._initObjects(node)
        self._logger.info("ObjectSerializer tool imported.")


class ObjectSerializerXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """XML importer and exporter for an object serializer.
    """
    adapts(IObjectSerializer, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = SER_NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        self._logger.info("%s serializer exported." % self.context.getId())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
        self._initProperties(node)
        self._logger.info("%s serializer imported." % self.context.getId())
