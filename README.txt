====================
CPSRelation - README
====================

$Id$


Features
========

CPSRelation provides features to manage relations between objects.

Interfaces have been defined to be able to use different types of graphs
storing and managing relations. Currently, graphs supported are:

- simple IOBTrees managing relations between integer unique identifiers and
  tuples of integer unique identifiers. This is the historical relations
  management, useful to store relations between CPS documents, using ther
  docid in the repository as unique integer identifiers.
- rdflib graphs managing RDF graphs provided by rdflib.
- Redland graphs managing RDF graphs provided by Redland using the python
  binding.

rdflib and Redland are required to use the two latter types of graphs, but
are not required for the product installation and use of simple graphs.

A tool (portal_relations) is able to manage several and different kinds of
graphs.

Another tool (portal_serializer) has been designed to provide object
serializations via pluggable TALES expressions. This tool currently requires
Redland to provide XML serializations following the RDF/XML syntax.


Installation notes
==================

Requirements
------------

CPSRelation requires:
- Zope (2.8.1 at least is recommended)
- CMF
- CPSInstaller
- CPSUtil


CPSRelation installation
------------------------

CMFQuickInstaller can be used to install this Zope product.

Otherwise, the usual way to install a CPS product applies:

- Log into the ZMI as manager
- Go to your CPS root directory
- Create an External Method with the following parameters:

    id            : cpsrelation_install (or whatever)
    title         : CPSRelation Install (or whatever)
    Module Name   : CPSRelation.install
    Function Name : install

- save it
- then click on the test tab of this external method


rdflib installation
-------------------

rdflib is a python library providing RDF related features.

Tests have been made using rdflib version 2.1.3 and Python version 2.3.5.

Please refer to the rdflib documentation and installation instructions at
http://rdflib.net


Redland installation
--------------------

Redland is a set of free software packages providing RDF related features,
written in C.

Packages are:

- Raptor RDF Parser Toolkit
- Rasqal RDF Query Library
- Redland RDF Application Framework
- Redland Language Bindings

Installation for CPSRelation requires the installation of Raptor, Rasqal,
Redland, and the Redland Python binding.

Tests have been made using versions:

- raptor-1.4.7
- rasqal-0.9.10
- redland-1.0.2.
- redland-bindings-1.0.2.1

Please refer to the Redland documentation and installation instructions at
http://librdf.org/.
