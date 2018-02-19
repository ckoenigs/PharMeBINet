#!/usr/bin/env python

###
# Takes an ontology in OBO file format and loads it into a neo4j database 
# instance

import argparse
# import neo4jrestclient
import oboparser

from twiggy import add_emitters, outputs, levels, filters, formats, emitters, log
from neo4jrestclient import options
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import query

__author__ = "Cesar Arze"
__copyyright__ = "Institute for Genome Science - University of Maryland School of Medicine"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Cesar Arze"
__email__ = "carze@som.umaryland.edu"

options.DEBUG = False
options.CACHE = True


def twiggy_setup():
    """
    Configures an instance of a twiggy logging object
    """
    obo_to_neo4j_output = outputs.FileOutput("tmp/ontology_to_neo4j.log",
                                             format=formats.line_format)
    rel_output = outputs.FileOutput("tmp/ontology_to_neo4j.relationships.log",
                                    format=formats.line_format)

    add_emitters(
        ("obo_to_neo4j", levels.INFO, None, obo_to_neo4j_output),
        ("relationships", levels.DEBUG, filters.msg_filter("RELATIONSHIP"), rel_output),
    )


def build_arg_parser():
    """
    Builds an argparse object to handle command-line arguments passed in.
    """
    parser = argparse.ArgumentParser(description="Loads an ontology file in " +
                                                 "OBO file format into a Neo4j graph database.")
    parser.add_argument('-i', '--input_obo_file', required=True,
                        help="The input OBO file")
    parser.add_argument('-s', '--neo4j_server_address', required=True,
                        help="The address to the Neo4j server. Must include port number")
    parser.add_argument('-t', '--typedefs', default="is_a", help="Typedefs that" +
                                                                 "that are present in this ontology. These will be used to define " +
                                                                 "the types of relationships supported in the input ontology")
    parser.add_argument('-r', '--root_node', required=True, action="append",
                        default=[], help='DOID\'s for any root nodes in this ontology')

    args = parser.parse_args()
    return args


def parse_typedefs_file(typedefsFile):
    """
    Parses the typedefs file containing the typedefs defined in the input 
    ontology file. These typedefs will be considered the valid relationships 
    that terms may use.
    """
    typedefs = []

    typedefsFh = open(typedefsFile)
    for typedef in typedefsFh:
        typedefs.append(typedef.strip())

    typedefsFh.close()
    return typedefs


def load_ontology_to_neo4jdb(db, ontology):
    """
    Loads the supplied ontology into a neo4j database. Returns a mapping of 
    neo4j node ID to ontology ID which will be utilized when creating 
    relationships in the neo4j database.
    """
    nodeMap = {}

    for term in ontology:

        if term.obsolete:
            log.info(' ** Skipping node %s because it is obsolete **' % term.name)
            continue
        log.info('Loading term %s...' % term.name)
        node = db.node()
        node.labels.add('DiseaseOntology')

        for (attr, value) in term.__dict__.items():
            if value and attr not in ["relationships", "synonyms"]:
                node.set(attr, value)
            elif value and attr == "synonyms":
                # Synonyms need to be converted from a list of tuples to a list
                # of strings
                synonymStrList = [" ".join(x) for x in value]
                node.set(attr, synonymStrList)

        nodeMap.setdefault(term.id, {})
        nodeMap[term.id]['node_id'] = node.id
        nodeMap[term.id]['relationships'] = term.relationships

        index_neo4j_node(db, node, term.id)

    return nodeMap


def index_neo4j_node(gdb, neo4j_node, term_id, category='ontologyid', key='id'):
    """
    Creates an index from a given Neo4j node to a category + id. This category
    allows for quick retrieval using non-Neo4j ID's. 
    """
    neo4j_index = gdb.nodes.indexes.create(category, type='exact', provider='lucene')
    neo4j_index.add(key, term_id, neo4j_node)


def create_term_relationships(db, mapping):
    """
    Creates the relationships between terms in our graph database
    that are present in our ontology. 
    """
    for term in mapping:
        # First check if we have a valid (set) of relationships for this term
        if mapping[term]['relationships']:
            nodeId = mapping[term]['node_id']
            childNode = db.node[nodeId]

            for (type, parentId, parentName) in mapping[term]['relationships']:
                parentNodeId = mapping[parentId]['node_id']
                parentNode = db.node[parentNodeId]
                childNode.relationships.create(type, parentNode)

                log.debug("RELATIONSHIP: parent %s --> child %s" % (parentName, childNode.get('name')))


def create_root_node_index(root_nodes, gdb):
    """
    Takes a list of root nodes (DOID's) from the command-line and 
    creates a Neo4j index to easily access them
    """
    ontology_index = gdb.nodes.indexes.get('ontologyid')
    root_index = gdb.nodes.indexes.create('rootnodes', type='exact', provider='lucene')

    for i in range(len(root_nodes)):
        neo4j_node = (ontology_index['id'][root_nodes[i]])[0]
        # TODO: Figure out a better way of doing this than casting int to string
        root_index.add('id', str(i), neo4j_node)


def main(parser):
    # Initialize logging
    twiggy_setup()

    # Parse our ontology file using our oboparser
    disease_ontology = oboparser.parse(parser.input_obo_file, parser.typedefs)

    # Load the OBO file into neo4j.
    # This will be performed in two steps, first the base nodes will 
    # be loaded into the neo4j database followed by the relationships.
    url = "http://localhost:7474/db/data/"
    user = "neo4j"
    password = "test"

    # gdb = GraphDatabase(parser.neo4j_server_address)
    gdb = GraphDatabase(url, user, password)
    print('connect')
    nodeMapping = load_ontology_to_neo4jdb(gdb, disease_ontology)
    print('nodes')
    create_term_relationships(gdb, nodeMapping)
    print('rel')

    create_root_node_index(parser.root_node, gdb)

    query='''Create CONSTRAINT ON ( diseaseontology:DiseaseOntology ) ASSERT diseaseontology.id IS UNIQUE'''
    gdb.query(q=query)


if __name__ == "__main__":
    main(build_arg_parser())
