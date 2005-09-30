====================
CPSRelation - README
====================

$Id$


Contents
========

* `Features`_
* `Installation notes`_

  - `Requirements`_
  - `CPSRelation Installation`_
  - `rdflib Installation`_
  - `Redland Installation`_


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

Additional information can be found in the doc/ directory.


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
- Create an External Method with the following parameters::

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

- Take care of library path settings when installing packages because rasqal
  requires raptor, and redland requires raptor and rasqal.
- packages like libxml2-dev and libdb4.3-dev, and a C++ compiler like g++
  may have to be installed too.

For information, our build summaries were:

Raptor build summary::

  RDF parsers available     : rdfxml ntriples turtle rss-tag-soup grddl
  RDF parsers enabled       : rdfxml ntriples turtle rss-tag-soup grddl
  RDF serializers available : rdfxml rdfxml-abbrev ntriples
  RDF serializers enabled   : rdfxml rdfxml-abbrev ntriples
  XML parser                : libxml(system 2.6.20)
  WWW library               : libxml(system 2.6.20)

Rasqal build summary::

  RDF query languages available : rdql sparql
  RDF query languages enabled   : rdql sparql
  Triples source                : raptor 1.4.7

Redland build summary::

  Berkeley/Sleepycat DB   : Version 4.3 (library db-4.3 in /usr/lib)
  Triple stores available : file hashes(memory) hashes(bdb 4.3)
  Triple stores enabled   : memory file hashes
  RDF parsers             : raptor(system 1.4.7)
  RDF query               : rasqal(system 0.9.10)
  Content digests         : md5(openssl) sha1(openssl) ripemd160(openssl)

Redland build summary (installing the Python binding)::

  Redland:              system 1.0.2
  Language APIs built:    python
