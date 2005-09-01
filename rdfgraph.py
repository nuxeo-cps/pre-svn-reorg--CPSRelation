# Copyright (c) 2004-2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# - M.-A. Darche
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

"""Graph.
"""

from zLOG import LOG, DEBUG, INFO

import os.path
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.PortalFolder import PortalFolder

from rdflib import Graph as rdflibGraph
from rdflib.backends import ZODB as ZODBBackend
from rdflib.backends import Sleepycat as SleepycatBackend
from rdflib.exceptions import UniquenessError

from Products.CPSRelation.interfaces.IGraph import IGraph
from Products.CPSRelation.graphregistry import GraphRegistry

class RDFGraph(UniqueObject, PortalFolder):
    """Graph.
    """
    __implements__ = (IGraph,)

    meta_type = 'RDF Graph'

    security = ClassSecurityInfo()

    #
    # API
    #

    def __init__(self, id, bindings={}, **kw):
        """Initialization

        kw are passed to be able to set the backend and other parameters
        """
        self.id = id
        self.rdf_store = ZODBBackend.ZODB()
        self.rdf_graph = rdflibGraph(self.rdf_store)
        for k, v in bindings.items():
            self.rdf_graph.bind(k, v)

        # Use this code if you want to use a BDB backend instead of the ZODB
        # backend.
        #
        # XXX: Note that if you want to use the BDB backend you should modify
        # this code so that the rdf_store is not persisted in the ZODB because:
        # 1. The Berkeley DB object cannot be persisted
        # 2. It would be stupid to persist the Berkeley DB object since all its
        #    information are already stored on the disk.
        #
        # Make sure that both rdf_store and rdf_graph are transient
        #self._v_rdf_graph = None
        #self._v_rdf_store = SleepycatBackend.Sleepycat()
        # You should create an "rdflib_db" directory in the "var" directory of
        # your Zope instance. This is where the BDB files will be stored.
        #bdb_dir_path = os.path.join(CLIENT_HOME, 'rdflib_db')
        #self._v_rdf_store.open(bdb_dir_path)

    security.declarePrivate('_getRDFGraph')
    def _getRDFGraph(self):
        """Get the RDF graph
        """
        if self.rdf_graph is None:
            self.rdf_graph = rdflibGraph(self.rdf_store)
        return self.rdf_graph

    security.declareProtected(View, 'serialize')
    def serialize(self, destination=None, format='xml', base=None):
        """Serialize the graph to destination

        If destination is None then serialization is returned as string.
        """
        rdf_graph = self._getRDFGraph()
        return rdf_graph.serialize(destination, format, base)

    security.declareProtected(View, 'listRelationIds')
    def listRelationIds(self):
        """List all the existing relations.
        """
        rdf_graph = self._getRDFGraph()
        items = {}
        # XXX AT: this is not uneffecient, optimization required...
        #for item in rdf_graph.predicates():
        #    items[item] = None
        #return items.keys()
        # Is it more efficient???
        try:
            set
        except NameError:
            from sets import Set as set
        predicates = set(rdf_graph.predicates())
        return list(predicates)

    security.declareProtected(ManagePortal, 'deleteAllRelations')
    def deleteAllRelations(self):
        """Delete all the relations.
        """
        rdf_graph = self._getRDFGraph()
        for triple in tuple(rdf_graph.triples((None, None, None))):
            rdf_graph.remove(triple)

    security.declareProtected(View, 'hasRelation')
    def hasRelation(self, relation_id):
        """Does the graph have a relation with the given id?
        """
        rdf_graph = self._getRDFGraph()
        relations = tuple(rdf_graph.triples((None, relation_id, None)))
        if relations:
            return 1
        else:
            return 0

    security.declareProtected(ManagePortal, 'addRelation')
    def addRelation(self, relation_id, **kw):
        """Add a relation with given id to the graph

        This is handled internally by the RDF graph when adding relations so do
        not do anything
        """
        pass

    security.declareProtected(ManagePortal, 'deleteRelation')
    def deleteRelation(self, relation_id):
        """Delete relation with given id from the graph

        All exiting relation instances for this relation will be deleted
        """
        rdf_graph = self._getRDFGraph()
        for triple in tuple(rdf_graph.triples((None, relation_id, None))):
            rdf_graph.remove(triple)

    # relation instances

    security.declareProtected(View, 'listAllRelations')
    def listAllRelations(self):
        """List all existing relation instances
        """
        rdf_graph = self._getRDFGraph()
        items = []
        for s, p, o in rdf_graph.triples((None, None, None)):
            items.append((s, p, o))
        return items

    security.declareProtected(View, 'hasRelationFor')
    def hasRelationFor(self, uid, relation_id):
        """Does the graph have a relation for the given object uid and the
        given relation type?
        """
        rdf_graph = self._getRDFGraph()
        objects = tuple(rdf_graph.objects(uid, relation_id))
        if objects:
            return 1
        else:
            return 0

    security.declareProtected(View, 'addRelationFor')
    def addRelationFor(self, uid, relation_id, related_uid):
        """Add relation to the given object uid for the given relation type
        """
        rdf_graph = self._getRDFGraph()
        rdf_graph.add((uid, relation_id, related_uid))

    security.declareProtected(View, 'deleteRelationFor')
    def deleteRelationFor(self, uid, relation_id, related_uid):
        """Delete relation for the given object uids and the given relation
        type
        """
        rdf_graph = self._getRDFGraph()
        rdf_graph.remove((uid, relation_id, related_uid))

    security.declareProtected(View, 'getValueFor')
    def getValueFor(self, uid, relation_id, related_uid=None,
                    default=None, any=False):
        """Get a value for given uid/relation_id, relation_id/related_uid or
        uid/related_uid pair.

        Exactly one of uid, relation_id or related_uid must be None.

        default is the value to be returned if no value is found.

        if any is True, return any value if more than one are found. If any is
        False, raise ValueError.
        """
        rdf_graph = self._getRDFGraph()
        try:
            retval = rdf_graph.value(uid, relation_id, related_uid,
                                     default, any)
        except UniquenessError, err:
            raise ValueError(err)
        return retval

    security.declareProtected(View, 'getRelationsFor')
    def getRelationsFor(self, uid, relation_id):
        """Get relations for the given object uid and the given relation type
        """
        rdf_graph = self._getRDFGraph()
        return tuple(rdf_graph.objects(uid, relation_id))

    security.declareProtected(View, 'getInverseRelationsFor')
    def getInverseRelationsFor(self, uid, relation_id):
        """Get relations for the given object uid and the inverse of the given
        relation type
        """
        rdf_graph = self._getRDFGraph()
        return tuple(rdf_graph.subjects(relation_id, uid))

    security.declareProtected(View, 'removeRelationsFor')
    def removeRelationsFor(self, uid, relation_id):
        """Remove relations for the given object uid and the given relation
        type
        """
        rdf_graph = self._getRDFGraph()
        for object in tuple(rdf_graph.objects(uid, relation_id)):
            rdf_graph.remove((uid, relation_id, object))

    security.declareProtected(View, 'removeAllRelationsFor')
    def removeAllRelationsFor(self, uid):
        """Remove all relations for the given object uid

        This is useful when deleting an object, for instance.
        """
        rdf_graph = self._getRDFGraph()
        for (predicate, object) in tuple(rdf_graph.predicate_objects(uid)):
            rdf_graph.remove((uid, predicate, object))
        for (subject, predicate) in tuple(rdf_graph.subject_predicates(uid)):
            rdf_graph.remove((subject, predicate, uid))

    #
    # ZMI
    #

    manage_options = (
        {'label': "Relations",
         'action': 'manage_editRelations'
         },
        # XXX AT: doc not ready yet
        #{'label': "Overview",
        # 'action': 'overview'
        # },
        ) + PortalFolder.manage_options[2:]

    security.declareProtected(ManagePortal, 'manage_editRelations')
    manage_editRelations = DTMLFile('zmi/rdfgraph_content', globals())

    security.declareProtected(ManagePortal, 'overview')
    overview = DTMLFile('zmi/rdfgraph_overview', globals())

    security.declareProtected(ManagePortal, 'manage_deleteAllRelations')
    def manage_deleteAllRelations(self, REQUEST=None):
        """Delete relations TTW."""
        self.deleteAllRelations()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url()
                                      + '/manage_editRelationInstances'
                                      '?manage_tabs_message=Deleted.')


InitializeClass(RDFGraph)

# Register to the graph registry
GraphRegistry.register(RDFGraph)
