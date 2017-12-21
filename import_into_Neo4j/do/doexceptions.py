#!/usr/bin/env python

##
# This custom Exception class should be raised whenever Lucene indices 
# are attempted to be generated to a directory that already exists. 
# The existance of a directory indicates that lucene indices already exist
# for this ontology file and we do not want them to be clobbered.
#

__author__ = "Cesar Arze"      
__copyyright__ = "Institute for Genome Science - University of Maryland School of Medicine"    
__license__ = "MIT"                  
__version__ = "1.0"                   
__maintainer__ = "Cesar Arze"                    
__email__ = "carze@som.umaryland.edu"    

class ExistingIndexDirectoryException(Exception):
    """
    """
    def __init__(self, value):
        self.error_msg = value

    def __str__(self):
        return repr(self.error_msg)
                
