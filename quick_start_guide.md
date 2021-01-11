# Quick start guide
**`oc_ocdm` is a Python package that enables the user to import, produce, modify and export RDF data structures which are
compliant with the [OCDM v2.0.1 specification](https://figshare.com/articles/Metadata_for_the_OpenCitations_Corpus/3443876).**

It's available on [PyPI](https://pypi.org/project/oc-ocdm/) and it's compatible with Python environments of version 3.7
or greater, since it makes a wide use of features like **Type Hints** [PEP 484](https://www.python.org/dev/peps/pep-0484/)
and **f-strings** [PEP 498](https://www.python.org/dev/peps/pep-0498/), along with many others.

Its first stable and feature-complete version (`4.0.0`) was released on early January 2021 by OpenCitations. Previous
development versions won't be published on online repositories, but they will always remain available as [tags in this
GitHub repository](https://github.com/opencitations/oc_ocdm/tags).

Before going any further with this explanation, it's highly recommended reading the OCDM specification implemented by
the package, since a good understanding on the meaning of the OCDM data structures and their relationships is required
to make a good use of the `oc_ocdm` package.

## Graph, Prov and Metadata
Data structures defined in the context of the OCDM are called _entities_. There are three different categories of
entities described by the specification:
  * *graph* entities: they represent the actual bibliographical data that has to be stored;
  * *provenance* entities: they are optionally used to keep track of how *graph* entities evolve over time, by storing
    a history of their subsequent snapshots;
  * *metadata* entities: they are used as a way to describe at a higher level the datasets and their different
    distributions.
    
The `oc_ocdm` package internal organization follows the same structure with three sub-packages called `oc_ocdm.graph`, 
`oc_ocdm.prov` and `oc_ocdm.metadata`, each one containing the respective class `GraphEntity`, `ProvEntity` and
`MetadataEntity`.

The only supported way of instantiating an entity object is by making use of the available factory classes: `GraphSet`,
`ProvSet` and `MetadataSet`. These classes act as a collection of entities, and they also provide factory methods to properly
instantiate them. Each one implements specific functionalities related to the role played inside the OCDM context by the
entities that they contain.

The most striking example is the `generate_provenance` method of `ProvSet`, which is able to automatically generate
snapshots of entities contained in a given `GraphSet`, leaving the user with nothing to do other than instantiating an
empty `ProvSet` and invoking this method with a proper `GraphSet` as input.

## Instantiating entities: how to
An entity object can be instantiated in three different ways:
  * **(case 1)** a brand-new entity can be created out-of-nothing by calling the corresponding factory method without passing any
    `res: URIRef` as input;
  * an already existing entity can be instantiated in two different ways, depending on the type of operations that the
    user wants to perform on it:
    * **(case 2)** manually importing the entity from a triplestore (or an RDF file) and passing the obtained `rdflib.Graph` to the
      `import_entities_from_graph` static method from the `Reader` class;
    * **(case 3)** instantiating the entity without providing any information about its preexisting state: this can be done by
      directly calling the corresponding factory method while passing the IRI of the existing entity as the `res: URIRef`
      parameter.
      
An entity with no knowledge of its preexisting state &mdash;either because it was created as in **(case 3)** or because it's a
completely new one&mdash; can only be modified in *append mode*. This means that, starting from an empty graph, the final set 
of triples that will have been produced by the user by invoking the *getter*, *setter* and *remover* methods of the entity
will be simply added to the already existing graph, whatever its current content is. Both in case of an RDF file storage
or of an online triplestore, the RDF semantics will automatically prevent the presence of duplicated triples: this means
that adding an already existing triple won't produce any effect. The user won't be notified in this particular case since,
for performance and simplicity reasons, no check is done on the already existing data before persisting the changes.

On the other hand, an entity containing a non-empty preexisting graph will be managed differently. Starting from an
empty graph, the final set of triples that will have been produced by the user by invoking the *getter*, *setter* and
*remover* methods of the entity will be compared with the preexisting graph to determine what triples must be added and
what must be removed from the ones that are currently stored. The user has the responsibility of providing an up-to-date
preexisting graph, in order to avoid any kind of problem related to this particular approach.

## General workflow
The following is a simple example of a general `oc_ocdm` workflow. For brevity considerations, only the processing of a
single entity will be shown, while the package is designed to handle multiple sets of several entities each at the same
time. For a more detailed documentation on how to invoke each function, please refer to the [package documentation](https://oc-ocdm.readthedocs.io/en/latest/).

Firstly, let's create a new entity. In this example, a `BibliographicResource` is created out-of-nothing.
``` python
from oc_ocdm.graph import GraphSet
my_graphset = GraphSet("http://dataset_base_iri/")
my_br = my_graphset.add_br("http://responsible_agent_uri/")
```

Then, let's add some info to the new `BibliographicResource` instance.
``` python
my_br.has_title("Resource title")
my_br.has_subtitle("Resource subtitle")
my_br.has_pub_date("2020-05-25")
from rdflib import URIRef
my_br.has_related_document(URIRef("http://related_document_uri/"))
```

The `has_pub_date` method requires as input a string in the ISO 8601 format, otherwise it won't work. A helper method is
provided by the package in order to simplify this task:
``` python
from oc_ocdm.support import create_date
iso_date_string = create_date([2020, 5, 25])
my_br.has_pub_date(iso_date_string)
```

Let's say that three errors where done in the previous steps:
  * a wrong title was given to the entity;
  * no subtitle should have been given to the entity;
  * a wrong related document was associated with the entity.

Since the title is a single-valued property of the entity, it's sufficient to just overwrite its value. On the other hand,
the related document property is a multi-valued one: this means that calling again the `has_related_document` will
simply add another related document without removing the incorrect one. Hence, in this case, it's necessary to also invoke
the `remove_related_document` method passing to it the value to be removed.
``` python
my_br.has_title("Correct title")
my_br.remove_subtitle()
my_br.remove_related_document(URIRef("http://related_document_uri/"))
my_br.has_related_document(URIRef("http://correct_uri/")
```

Let's say that the user needs to also create a provenance layer of snapshots describing these changes.
``` python
from oc_ocdm.prov import ProvSet
my_provset = ProvSet(my_graphset, "http://dataset_base_iri/")
my_provset.generate_provenance()
```

The dataset modification date must be updated too.
``` python
from oc_ocdm.metadata import MetadataSet
my_metadataset = MetadataSet("http://dataset_base_iri/")
my_dataset = my_metadataset.add_dataset("dataset name", "http://dataset_base_iri/")
my_dataset.has_modification_date("2020-01-01T00:00:00")
```

It's now time to persist the changes made to the entity back to the online triplestore or to the RDF file (or both).
``` python
from oc_ocdm import Storer
my_graph_storer = Storer(my_graphset)
my_prov_storer = Storer(my_provset)
my_metadata_storer = Storer(my_metadataset)
my_graph_storer.upload_all("http://triplestore_endpoint_url/")
my_prov_storer.upload_all("http://triplestore_endpoint_url/")
my_metadata_storer.upload_all("http://triplestore_endpoint_url/")
```

Finally, if the user wants to continue modifying the same entities, then it's necessary to invoke the `commit_changes`
method of `GraphSet` and `MetadataSet`. This will align again the internal state of the contained entities with their
persisted counterparts, enabling the user to consistently apply further changes to them.
``` python
my_graphset.commit_changes()
my_metadataset.commit_changes()
```
