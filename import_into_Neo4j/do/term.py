#!/usr/bin/env python

##
# A class that represents an individual term in an ontology. The Term class
# contains the following attributes:
#     
#             * id
#             * name
#             * synonym
#             * relationships
#             * xrefs
#             * alternate id
#             * definition
#             * subset
#

__author__ = "Cesar Arze"      
__copyyright__ = "Institute for Genome Science - University of Maryland School of Medicine"    
__license__ = "MIT"                  
__version__ = "1.0"                   
__maintainer__ = "Cesar Arze"                    
__email__ = "carze@som.umaryland.edu"    

class Term():

    def __init__(self, **kwargs):
        """
        Constructs a Term object. 
        """
        self.id = ""
        self.name = ""
        self.definition = ""
        self.synonyms = []
        self.relationships = []
        self.xrefs = []
        self.alternateIds = []
        self.subsets = []
        self.obsolete = False

        # If a set of keyword args are passed in along with the constructor 
        # call we set all attributes to their values.
        if kwargs:
            self.termId = kwargs.get('id')
            self.name = kwargs.get('name')
            self.definition = kwargs.get('def')
            self.synonyms = kwargs.get('synonyms')
            self.relationships = kwargs.get('relationships')
            self.xrefs = kwargs.get('xrefs')
            self.alternateIds = kwargs.get('alternateIds')
            self.subsets = kwargs.get('subsets')
            self.isObsolete = kwargs.get('isObsolete')                           
