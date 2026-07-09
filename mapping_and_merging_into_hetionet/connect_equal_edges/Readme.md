This script generates relationships between the different kinds of phenotypes. This includes SE-symptom, SE-disease, symptom-disease, and SE-phenotype.

The SE-symptom edges use:
    Name mapping
    Mapping with xref UMLS cui to SE identifier
    Mapping Mesh to UMLS CUI and trying to map to SE identifier

The SE-disease edges use:
    Disease external identifiers from UMLS are mapped to SE identifier
    The disease external identifier from MedDRA is mapped to the SE external identifier
    Name mapping
    Synonym of disease to SE name
    Disease name to UMLS to get UMLS CUI and map to SE identifier

The symptom-disease edges use:
    The disease external identifier from HPO is mapped to the symptom external identifier HPO
    Disease UMLS cui to symptom xref UMLS cui
    Name mapping

The SE-phenotype edge used as mapping:
    External identifier UMLS CUI from phenotype to SE identifier
    External identifier MedDRA ID from phenotype to SE external identifier
    Name mapping
    Synonyms of phenotype to SE name
    Phenotype name to UMLS to get UMLS CUI and map to SE identifier
              
All the mapping pairs are written into a TSV file and for each label pair, a cypher query is generated and written into a cypher file.
In the end, the information is integrated into the database with the cypher shell.


Next, connections between compound and metabolite are generated:
    First, load all compound information.
    Then the metabolite information is asked and used for mapping. One is the InChIKey and the other a combination of the DrugBank identifier and name mapping.
    All pairs are written into a TSV file and a cypher query is generated and added to the cypher file.

In the following, a programm is executed that calculates between all compounds the similarity:
    First, prepare the structure file into the format of RDKIT and pybel.
    Next, prepare the different fingerprints of the different toolkits.
    Then, generate a TSV file for all pairs with all values of the different similarities.

The last program it runs through the similarity calculation and check for above a filter and generate a subset of all pairs:
    For each, fingerprint-metric pari an own threshold is defined which is based on 1% rule of all data.
    All pairs whee at least on is above a threshold is added to the subset.
    Additionally, a cypher file is generated.    

In the last step, the similarity relationships are integrated into the database with the cypher-shell.
