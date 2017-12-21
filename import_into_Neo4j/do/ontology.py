#!/usr/bin/env python

##
# A class representing an Ontology file. This class consisits of Term
# objects that represent the individual terms in an ontology
#

import term

__author__ = "Cesar Arze"      
__copyyright__ = "Institute for Genome Science - University of Maryland School of Medicine"    
__license__ = "MIT"                  
__version__ = "1.0"                   
__maintainer__ = "Cesar Arze"                    
__email__ = "carze@som.umaryland.edu"    

class Ontology():

    def __init__(self):
        """
        Construct an Ontology object. The Ontology class contains three
        attributes: terms, typedefs and metadata
        
        The terms attribute houses all the terms found in this ontology
        in a dictionary for quick lookups. Typedefs are stored in a list
        as they do not require quick lookup and merely are stored to provide the 
        relationship types that are present in this ontology. The metadata attribute
        houses any metadata (version, namespace, etc) found in this ontology in a 
        key - value pair format.
        """
        self.terms = {} 
        self.typedefs = set()
        self.metadata = []

    def __iter__(self):
        """
        Generator an iterator to iterate over our Ontology object. Iterating
        over the Ontology object is akin to iterating over the terms dictionary
        """
        return self.terms.values().__iter__()

    def __len__(self):
        """
        Returns the length of our terms dictionary + the length of our metadata
        list
        """
        return len(self.terms) + len(self.metadata)

    def __contains__(self, v):
        """
        Returns True or False depending on whether or not the id passed in
        exists in the terms dictionary
        """
        return v in self.terms

    def __getitem__(self, v):
        """
        Returns the term associated with the passed in term ID.
        """        
        return self.terms[v]

    def add_term(self, term):
        """
        Adds a term to the ontology dictionary. The object passed
        into this function must be of type Term.
        """
        # TODO: Write custom exception class and test to ensure the
        # object passed into this function is of type Term
        termId = term.id
        self.terms[termId] = term
        
    def get_term(self, termID):
        """
        Retrieves a term in this ontology using the term ID. 
        """        
        return self.terms.get(termID, None)

    def get_terms(self):
        """
        Retrieves all terms found in this ontology. This function returns a
        list of all terms as opposed to the dictionary they are stored in.
        """
        return self.terms.values()

    def get_term_ids(self):
        """
        Retrieves a list of all term ID's found in this ontology
        """        
        return self.terms.keys()

    def add_typedef(self, typedef):
        """
        Add a single typdef to the typdefs attribute. If this typedef already
        exists in the typedefs attribute it will not be added.
        """
        self.typedefs.update(typedef)

    def get_typedefs(self):
        """
        Retrieves all typedefs found in this ontology
        """
        return list(self.typedefs)
