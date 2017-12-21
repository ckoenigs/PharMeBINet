#!/usr/bin/env python

###
# This module handles parsing of an OBO (ontology) file format into a
# representative Ontology class which allows for easy access to terms
# and their attributes

import re

import itertools
from itertools import groupby
from ontology import Ontology
from term import Term

__author__ = "Cesar Arze"      
__copyyright__ = "Institute for Genome Science - University of Maryland School of Medicine"    
__license__ = "MIT"                  
__version__ = "1.0"                   
__maintainer__ = "Cesar Arze"                    
__email__ = "carze@som.umaryland.edu"    

class TermMissingRequiredFieldException(Exception):
    """
    A custom exception class that should be raised when one of the required 
    fields (id, name)
    """
    def __init__(self, value):
        self.error_msg = value

    def __str__(self):
        return repr(self.error_msg)
                
def parse(oboFile, typedefs):
    """
    Parses an OBO (ontology file) creating a correspoinding Ontology 
    object composed of Term objects that relate to the terms found in the
    ontology file.
    """
    ontology = Ontology()

    ## Use groupby to group the lines of our file into chunks of text, some 
    ## stanzas, some typedefs, and other metadata to be processed 
    with open(oboFile) as f:
        for (key, group) in groupby(f, is_data):
            if key:
                #print(group)
                #header = group.next().rstrip('\n')
                header = group.__next__().rstrip('\n')
                
                

                if header.find('[Typedef]') != -1:
                    dataDict = get_data_as_dict(group)
                    ontology.add_typedef(dataDict['name'])
                elif header.find('[Term]') != -1:
                    dataDict = get_data_as_dict(group, typedefs)
                    ontology.add_term(build_term(dataDict))
                else:                    
                    # We are dealing with ontology metadata that should be 
                    # captured in our ontology object.
                    ontology.metadata.append(header)
                    ontology.metadata.extend([x.strip() for x in group])

    return ontology               

def is_data(line):
    """
    Function utilized by itertool's groupby method in determining 
    the delimiter between our blocks of data.
    """
    return True if line.strip() else False

def get_data_as_dict(data, typedefs=None):
    """
    Parses a stanza of text to produce a dictionary housing all our 
    attributes. The text being parsed must be in in format (<KEY>: <VALUE>)
    """
    term = {}

    for item in data:
        (key, value) = [x.strip() for x in item.split(":", 1)]

        # We need to account for any of the typedefs in our ontology which are
        # defined in the typedefs list passed into this function. We are 
        # dumping all of these typedefs under the 'relationship' key as they all
        # are the relations between our nodes
        if typedefs and key in typedefs:
            (parentId, parentName) = [x.strip() for x in value.split('!')]
            value = (key, parentId, parentName)
            key = "relationship"

        if key in term:
            # If this term already exists in our dictionary we want to
            # create a list housing the previous value(s) alongside the
            # new value
            term[key].append(value)
        else:
            # Otherwise just add the value normally
            term[key] = [value]
    
    return term

def build_term(dict):
    """
    Builds a Term object from the term metadata dictionary provided.
    """
    # Add our metadata to our term piece-by-piece
    term = Term()

    try:
        term.id = dict['id'][0]
        term.name = dict['name'][0]
    except KeyError as k:
        raise TermMissingRequiredFieldException("Missing required field %s" % k)

    termDef = dict.get('def', [""])
    term.definition = termDef[0]
    obsoleteBool = dict.get('is_obsolete', [False])
    term.obsolete = obsoleteBool[0]

    term.synonyms.extend( format_synonym_list(dict.get('synonym', [])) )
    term.relationships.extend( dict.get('relationship', []) )
    term.xrefs.extend( dict.get('xref', []) ) 
    term.alternateIds.extend( dict.get('alt_id', []) )
    term.subsets.extend( dict.get('subset', []) )

    return term

def format_synonym_list(synonyms):
    """
    Take our raw synonym list and break it up into a tuple containing the
    following three elements:

                (<SYNONYM NAME>, <SYNONYM TYPE>, <SYNONYM ID>)
    """        
    synonymList = []
    
    # Synonym needs to be peeled into components using a reuglar expression
    pattern = re.compile(r'"(.+)" (\w+) \[(.*)\]')
    for synonym in synonyms:
        synonymMatch = re.match(pattern, synonym)       
        name = synonymMatch.group(1)
        type = synonymMatch.group(2)
        id = synonymMatch.group(3)

        synonymList.append( (name, type, id) )

    return synonymList
