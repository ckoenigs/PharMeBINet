The script to merge MarkerDB information into PharMeBINet

First, the MarkerDB chemical is mapped to metabolite:
    First, load the metabolite into dictionaries.
    Then, generate the mapping TSV file and create a cypher file with the additional mapping query.
    Next, the MarkerDB chemicals are loaded and are mapped:
        
        First, it is mapped with HMDB ID to metabolite.
        Then manual mappings are executed.
        Last, the chemical names are mapped to metabolite.
    All mapping pairs are written into the TSV file.

Next, the MarkerDB conditions are mapped to disease, symptom, side effect, and phenotype:
    First, load the information for disease, symptoms, and phenotype into dictionaries.
    Create a mapping TSV file and add a mapping cypher query to the cypher file.
    The conditions are loaded and mapped:
        
        First, map the name to the disease name.
        Then, map the name to the symptom name.
        Next, map the name to the phenotype name.
        In the following, manual mapping to disease is used.
        Then, map the condition to the disease with umls cui.
        The name is mapped to disease synonyms.
        The same is done for symptoms in the same order and for phenotype.
        Next map name to umls cui to ncit ant to disease ncit xref.
        Map with umls cui to synonyms in umls to disease name.
        Same to symptom and then to phenotype.

    All mapping pairs are written into the TSV file.

[//]: # (The same but with OMIM ID to disease OMIM xref.)
[//]: # (Map condition to symptom with umls to OMIM to symptom OMIM xref.)
[//]: # (Map with umls OMIM ID to phenotype identifier.)


In the following the MarkerDB sequence variant is mapped and added to the variant:
    First, load variant information into different dictionaries.
    Next, generate TSV files for mapping, and new nodes with the additional cypher queries are added to the cypher file.
    Next, the sequence variants are mapped:
        
        First, use the external link to map to the variant with the clinvar ID.
        Next, the rs id is mapped to the variant dbsnp id but better with the name also mapped to the same variant else only the dbSNP id.
        Then, it is mapped with name and location equal to the variant name and position.
    The mapping pairs are written into the TSV file and the not mapped nodes with rs id are written into the new node TSV.

The last mapping is MarkerDB protein to protein:
    First, the PharMeBINet proteins are loaded and the information is written into dictionaries. This included the gene-protein connection.
    Next, the TSV file is created and the cypher query is added to the cypher file.
    Then, the proteins of MarkerDB are mapped:
        
        First, the umls ID is mapped to the protein. Except for nodes with the IDs ()"P01860", "Q969X2", "Q13609"), they are wrong and 21 nodes have one of these ids.
        Next, the name is mapped to the protein name.
        Last, the gene name is mapped to the gene connected to the mapped protein.
    All mapping pairs are written into the TSV file.

The mappings are integrated into the database with neo4j cypher-shell.

In the last program, prepare the edges from MarkerDB which includes information variant-phenotype/protein-phenotype/metabolite-phenotype:
    First, a cypher file is generated.
    Then, the following steps are executed for variant, protein, and metabolite:
    For disease/symptom/SE/phenotype, TSV files are generated with the additional cypher queries.
    Also, existing edges are loaded and written into a dictionary.
    Load the pairs and add the information inot a dictionary seperated by the labels disease, symptom, SE and phenotype and add the rela info as edge. Some additonal information are added to the relationship like edge type, marker id for the url and the reference.
    Next, it iterated throught the dictionary and combine relationships information for one pair and extract the the reference information. These information are written into a TSV file.


The last step is to integrate the different edge information into the database with the Neo4j cypher shell.