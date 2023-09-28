The script to merge HPO information into the database contains multiple steps:
First, the HPO diseases are mapped to the disease:
               First, the database diseases are loaded into a dictionary.
               With threads, the HPO diseases (that are not is_obsolete=true) are mapped to disease. If the HPO disease is from DECIPHER then it is mapped by name and synonyms to disease name and synonyms. If this did not work then try to get a UMLS Cui from UMLS by name and map to disease external references UMLS Cui. In case the disease is from OMIM  the first mapping is the OMIM id to the disease's external reference OMIM ID.  If this did not work it tries to map with the use of UMLS by name and OMIM ID to UMLS Cui to disease UMLS Cui.  The ones that did not map are mapped with name and synonym to disease name and synonyms.  For a disease with source, ORPHA is first mapped with ORPHA ID to disease external reference ORPHA identifier. If this did not work it is tried to map with name/ synonym to disease name and synonyms. 
               All pairs that are mapped are written into TSV files.

Next, the HPO phenotypes are mapped to Symptoms:
            First, the mapped and new node files are generated. Additionally, the cypher queries integrate the different nodes and the is-a relationship.
            I took from HPO only the phenotypes which are part of the Phenotypic abnormality (HP:0000118) hierarchy as symptoms to map and the ones that do not map generate a new node with HPO id as an identifier. The mapping is based on name mapping. The next mapping method is mapping the HPO phenotype synonyms to names of symptoms All pairs are written into a dictionary. The not mapped nodes are written into the new node TSV file.
            The mapped pairs are written into the other TSV file.

The cypher-shell integrates the merged node information into the database.
Now the different kinds of relationships between disease and symptoms are prepared.
               First, all symptoms are loaded.
               Then, all existing disease-symptoms present pairs are loaded.
               Next, the TSV files for new and updated relationships are generated. Additionally, The cypher queries and the cypher file are generated.
               Next, only the relationships which have the aspect phenotypic abnormality are added to the TSV files.
               The last step is that the relationship inheritance information is added to the disease node as an own property as an inheritance (something like autosomal dominant). This is written into a TSF file and a cypher query is added to add this information to the disease node.