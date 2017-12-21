#!/usr/bin/env python

##
# This script indexes the Disease Ontology HumanDO.obo file. 
#

import os
import lucene
import argparse
import oboparser
import ConfigParser

from doexceptions import ExistingIndexDirectoryException

__author__ = "Cesar Arze"      
__copyyright__ = "Institute for Genome Science - University of Maryland School of Medicine"    
__license__ = "MIT"                  
__version__ = "1.0"                   
__maintainer__ = "Cesar Arze"                    
__email__ = "carze@som.umaryland.edu"    

def build_arg_parser():
    """
    Creates an argparser object to handle any command-line arguments passed
    to this script.
    """
    parser = argparse.ArgumentParser(description='Indexes ontology files found'
                + ' in the specified directory.')
    parser.add_argument('-d', '--do_obo', required=True, help='The disease'
                + ' ontology obo file.')                    
    parser.add_argument('-o', '--output_index_dir', required=True, help='The desired'
                + ' output index directory where lucene index files will be store.')
    parser.add_argument('-m', '--xref_mapping', required=True, help='An optional mapping file to allow'
                + 'for simplification of xref identifiers')
    args = parser.parse_args()
    
    return args

def replace_xref_identifier(xref_val, xref_map):
    """
    Takes an xref value and attemps to shorten the string to a simplified xref 
    identifier.
    
    E.x. SNOMED_2011_10_22:226730 translates to SNOMED:226730        
    """
    (xref_ident, _ignore) = xref_val.split(':')

    if (xref_map.has_option('xref', xref_ident)):
        xref_val = xref_val.replace(xref_ident, xref_map.get('xref', xref_ident))

    return xref_val 

def index_ontology_files(oboFile, outDir, xref_map):
    """
    Iterates over our list of ontology files and creates an index for each file.
    """
    lucene.initVM()
    analyzer = lucene.StandardAnalyzer(lucene.Version.LUCENE_CURRENT)
    
    # Handle a little bit of lucene setup
    filename, _ext = os.path.splitext( os.path.basename(oboFile) )

    indexDir = os.path.join(outDir, filename)
    if os.path.exists(indexDir):
        raise ExistingIndexDirectoryException('Error, attempted to index same file twice or index two files named the same')

    dir = lucene.SimpleFSDirectory(lucene.File(indexDir))
    writer = lucene.IndexWriter(dir, analyzer, True, lucene.IndexWriter.MaxFieldLength(512))

    for term in oboparser.parse(oboFile, ['is_a']):
        if term.obsolete:
            continue

        doc = lucene.Document()
        add_field_to_document(doc, "term id", term.id, lucene.Field.Store.YES, lucene.Field.Index.ANALYZED)
        add_field_to_document(doc, "name", term.name, lucene.Field.Store.YES, lucene.Field.Index.ANALYZED, 4.0)

        # Frequently in the definition text we will run into URLs or some sort of hyperlinks that could 
        # query hits that we would not want to occur thus errantly increasing the score of the field.
        # We will strip out these hyperlinks and index just the text.
        add_field_to_document(doc, "definition", strip_urls_from_text(term.definition), lucene.Field.Store.YES, lucene.Field.Index.ANALYZED, 0.4)

        # Synonyms, relationships, xrefs, subsets, and alternate ID's are all represented as lists
        # in our Ontology object and need to be entered in one at a time
        add_fields_to_document(doc, "synonym", [x[0] for x in term.synonyms if x], 
                               lucene.Field.Store.NO, lucene.Field.Index.ANALYZED, 0.7)

        add_fields_to_document(doc, "alt_id", term.alternateIds, lucene.Field.Store.NO, lucene.Field.Index.ANALYZED)
        add_fields_to_document(doc, "xref", [replace_xref_identifier(x, xref_map) for x in term.xrefs], lucene.Field.Store.NO, lucene.Field.Index.ANALYZED)
        add_fields_to_document(doc, "relationship", [" ".join(list(x)) for x in list(term.relationships)],
                               lucene.Field.Store.NO, lucene.Field.Index.NOT_ANALYZED)
        add_fields_to_document(doc, "subset", term.subsets, lucene.Field.Store.NO, lucene.Field.Index.ANALYZED)
        writer.addDocument(doc)

    writer.optimize()
    writer.close()        

def strip_urls_from_text(definition):
    """
    Strips URLs from the definition text and returns a clean URL to be index by Lucene
    """
    def_text = None
    print definition
    
    if definition:
        (_ignore, def_text, urls) = definition.split('"', 2) 

    return def_text if def_text else definition

def add_field_to_document(document, field_name, value, store, analyzed, boost=None):
    """
    Adds a field to the passed in Lucene document. If the boost kwarg is passed
    in the field will be boosted by the specified value.
    """
    field = lucene.Field(field_name, value, store, analyzed)

    if boost:
        field.setBoost(boost)

    document.add(field)

def add_fields_to_document(document, field_name, values, store, analyzed, boost=None):
    """
    Iterates over a list of values and adds them to the document at the specified field.
    """ 
    for v in values:
        add_field_to_document(document, field_name, v, store, analyzed, boost)

def main(parser):
    oboFile = parser.do_obo
    outputDir = parser.output_index_dir
    xref_mapping = ConfigParser.SafeConfigParser()
    xref_mapping.read(parser.xref_mapping)

    # Create lucene indices for each obo file
    index_ontology_files(oboFile, outputDir, xref_mapping)

if __name__ == "__main__":
    main(build_arg_parser())
