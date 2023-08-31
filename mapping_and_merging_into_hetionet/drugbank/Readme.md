The DrugBank merging has two scripts because of the order in how the data are merged into the database. In the first script the drugs, salt, product, and gene variants. The second one is to integrate the protein and targets.

Script one defines the license of DrugBank. Following steps:
Mapping of drug and preparation of drug interaction:
    First, get all properties of the DrugBank drug to generate the TSV files (mapped and new nodes) with the different properties.
    Then, load all existing compounds and write information into the dictionary.
    Next, the DrugBank compounds are loaded and written into a dictionary.
    In the following, all interaction edges of DrugBank are loaded and written into a dictionary.
    Then, the DrugBank compounds are mapped to the compounds with DrugBank ID and alternative ID. All pairs are written in TSV files. If one DrugBank node is mapped to multiple nodes one pair is written in the TSV file and the rest are added to a merge script so that all information from one node is integrated into another with additional also add the relationships from this node. If no mapping appears they are written into the TSV file for new nodes.
    Next, the cypher queries to integrate the mapped node information and the new node are generated and written into the cypher file.
    In the last step, the cypher query to integrate drug-drug interaction (DDI) is generated. Also, the DDIs are integrated into a TSV file.

Next, the drug information and edges are integrated into the database with the Neo4j cypher-shell.
In the following, the merge node script is executed.

Then, Salt mapping to Compound:
    First, find all compounds that did not map to DrugBank drugs and write information into dictionaries.
    Next, get all properties of salt nodes and prepare a cypher query to integrate salt nodes into the database. Also, TSV files for the nodes and relationships are generated. Furthermore, the cypher query for integrating the relationships between compound and salt is added to the cypher file. Additionally, a cypher file is generated to delete all Compounds which are not mapped.
    Then, all salt nodes are written into the TSV file. All compounds that map with InChIKey and or name are added to the merge script to be combined into the salt node.
    In the last step, the relationship pairs between salt and compound are written into the TSV file.

Next, the Product:
    First, prepare the TSV file to integrate the products.
    Next, prepare cypher queries for integrating the product nodes (first, get the properties of the product) and the integration of product-compound relationships. They are all written in the cypher files from the salt program.
    In the last step, the product identifiers are written into the TSV file additional the URL is generated depending on the identifier source.


In the following, the DrugBank gene variant is mapped to the variant:
    First, load all variants from the database and write information into dictionaries.
    Then, generate the mapping TSV and new node TSV. Also, the cypher queries for mapping and generating new nodes are generated and added to the cypher file.
    For the mapping is used dbSNP identifier of the drugbank gene variant to the external reference dbSNP identifier of the database. Next, mapping is allele name to database variant name.  All that did not map, but have an rs identifier (dbSNP identifier) are added to the TSV file for the new node.

Then, the DrugBank pathways are mapped to pathways:
    First, load all pathway information and write them into dictionaries.
    Second, the mapping TSV file is prepared and the cypher query is added to the cypher file.
    Next, the DrugBank pathways are loaded and mapped:
        The first mapping method is the SMPDB identifier to the xref smpdb id of the pathway.
        Secondly, is the mapping with name to name of the pathway.
    All mapping pairs are written into the TSV file.
    Then, a TSV file is prepared for compound-pathway edges and the additional cypher query is added to the cypher file.
    The last step is to get all pairs and write them into the TSV file.

Next, the DrugBank metabolites are mapped to metabolites:
    First, load all metabolites and write information into dictionaries.
    Secondly, the mapping TSV file and the cypher file are generated.
    In the last step, the DrugBank metabolites are loaded  and mapped:
        First, mapping is with InChIKey.
        Next, mapping is with SMILES.
        The last mapping is with name mapping.
    All mapping pairs are written into the TSV file.

The node information and the relationships are integrated into the database with Neo4j cypher-shell.

In the following, the merge node script of the salt is executed.

The variant-compound edge needs its own program:
    First, prepare the TSV file for variant-compound pairs and the cypher query to integrate the pairs into the database.
    Next, load all compound-variant pairs and relationships into a dictionary. Then before writing into the TSV file, the relationship pairs information are combined.

These relationships are integrated into the database with cypher-shell.

The next cypher file deletes all compounds which are not mapped.

The last program is the preparation of similarity between the compounds:
    First, prepare the structure file into the format of RDKIT and pybel.
    Next, prepare the different fingerprints of the different toolkits.
    Then, generate a TSV file for all pairs with all values of the different similarities. Also, the cypher query is generated.  In the following, all similarity metrics are used for all fingerprint combinations if possible. Only the pairs with a given similarity value over a threshold are saved.

In the last step, the similarity relationships are integrated into the database with the cypher-shell.
               
               
The second script focused on mapping and merging the protein/targets into the database.

The mapping of protein/target to Protein and chemical:
    First, load all chemicals into the program.
    I did generate a manually checked list of all targets that do not have a Uniprot ID if they are a protein or not. This information is loaded into the program.
    Next, load all Proteins.
    Then generate the cypher files to integrate the mapping between DrugBank protein and protein and DrugBank target and chemical. Also, cypher queries are generated to give the mapped node additional labels like Target, Enzyme, Carrier, and Transporter. Moreover, the TSV file for the different mappings is generated.
    Next, the DrugBank proteins/targets are mapped to proteins with the UniProt identifier. If it is not mapped and in the human, it is mapped to chemicals by name. After that, it is tried to be mapped to protein by name. All, mapped pairs are written into the TSV file.
    After this, I tried to integrate the component relationship of DrugBank but because the protein which has multiple components has no UniProt identifier information this information is not integrated.

Next, is DrugBank PC mapping to PC:
    First, load all PC information into dictionaries.
    Next, generate the mapping TSV files and add the cypher query to the cypher file.
    Then, load all PCs of DrugBank and map them to PCs:
        First, mapping is with mesh id to PC xref mesh id.
        Then, it maps with name to the PC name.
        The next mapping method is with the use of UMLS and name to get a UMLS CUI to the PC xref UMLC CUI.
        The last mapping is with mesh ID in UMLC to get a UMLS CUI and map to PC xref UMLS CUI.
    All mapping pairs are written into the TSV file.
               
Integrate the mapping of protein, PC, and target into the database with cypher-shell.

Prepare the relationships between 'compound-protein/target':
    First, take all  compound-protein/target (chemical) pairs where the relationship is in the human and have references and add them to a dictionary
    Then, go through all relationship pairs of the different relationship types and generate TSV files and cypher queries to integrate the information into the database. In the following, the pair information is written into the TSV file. If multiple edges with the same relationship type exist the information is combined and written into the TSV file.

Prepare the DrugBank reaction between chemicals, and metabolites with the use of proteins:
    First, load all protein identifiers and add them into a set.
    Second, create a TSV file and cypher for the node-edge Reaction. The left and right elements of the reactions get TSV files for metabolites, proteins, and compounds with additional cypher queries. The same is done for protein-reaction edges.
    For all combinations of compound and metabolite in the reaction, the following steps were used:
        Load all connections in this direction where no proteins take part. Write all pairs of compound/metabolite-reaction pairs for the right type into a TSV file and add all reaction node IDs to another TSV file.
        Next, all connections are loaded where enzymes take place in the reaction. First, the enzymes are mapped to the protein and only if all are mapped this reaction is considered. The same steps as before are executed with the addition of filling the protein-reaction edge TSV file.

Merge the pc-compound edge into PharMeBINet:
    First, generate the TSV file and the additional cypher query.
    Then, load all pairs and write them into the TSV file.


Integrate the protein/target-compound relationship with Neo4j cypher-shell.