The DrugBank merging has two scripts because of the order in how the data are merged into the database. In the first script the drugs, salt, product, and gene variants. The second one is to integrate the protein and targets.

Script one defines the license of DrugBank. Following steps:
Mapping of drug and preparation of drug interaction:
               First, get all properties of the DrugBank drug to generate the TSV files (mapped and new nodes) with the different properties.
               Load all node and interaction information from Neo4j.
               Map DrugBank drugs to database compound with DrugBank identifier and alternative DrugBank identifier. All pairs are written in TSV files. If one DrugBank node is mapped to multiple nodes one pair is written in the TSV file and the rest are added to a merge script so that all information from one node is integrated into another with additional also add the relationships from this node. If no mapping appears they are written into the TSV file for new nodes.
               Next, the cypher queries to integrate the mapped node information and the new node are generated and are written into the cypher file.
               In the last step, the cypher query to integrate drug-drug interaction (DDI) is generated. Also, the DDIs are integrated into a TSV file.

Next, the drug information and edges are integrated into the database with cypher-shell.
In the following, the merge node script is executed.
Then, Salt mapping to Compound:
               First, find all compounds that did not map to DrugBank drugs.
               Next, get all properties of salt nodes and prepare a cypher query to integrate salt nodes into the database. Also, TSV files for the nodes and relationships are generated. Furthermore, the cypher query for integrating the relationships between compound and salt is added to the cypher file. Additionally, a cypher file is generated to delete all Compounds which are not mapped.
               Then, all salt nodes are written into the TSV file. All compounds that map with InChIKey and or name are added to the merge script to be combined into the salt node.
               In the last step, the relationship pairs between salt and compound are written into the TSV file.
Next the Product:
               First, prepare the TSV file to integrate the products.
               Next, prepare cypher queries for integrating the product nodes (first, get the properties of the product) and the integration of product-compound relationships. They are all written in the cypher files from the salt program.
               In the last step, the product identifiers are written into the TSV file additional the URL is generated depending on the identifier source.
In the following the DrugBank gene variant is mapped to variant:
               First, load all variants from the database.
               Then, generate the mapping TSV and new node TSV. Also, the cypher queries for mapping and generate new nodes are generated and add to the cypher file.
               For the mapping is used dbSNP identifier of the drugbank gene variant to the external reference dbSNP identifier of the database. Next, mapping is allele name to database variant name.  All that did not map, but have an rs identifier (dbSNP identifier) are added to the TSV file for the new node.
The node information and the relationships are integrated into the database with cypher-shell.
In the following, the merge node script of the salt is executed.
The variant-compound edge needs an own program:
               First, prepare the TSV file for variant-compound pairs and the cypher query to integrate the pairs into the database.
               Next, load all compound-variant pairs and relationships into a dictionary. Then before writing into the TSV file the relationship pairs information are combined.
These relationships are integrated into the database with cypher-shell.
The next cypher file deletes all compounds which are not mapped.
The last program is the preparation of similarity between the compounds:
               First, prepare the structure file into the format of RDKIT and pybel.
               Next, prepare the different fingerprints of the different toolkits.
               Then, generate a TSV file for all pairs with all values of the different similarities. Also, the cypher query is generated.  In the following, all similarity metrics are used for all fingerprint combinations if possible. Only the pairs with a given similarity value over a threshold are saved.
In the last step, the similarity relationships are integrated into the database with the cypher-shell.
               
               
The second script focused on mapping and merging the protein/targets to the database.
The mapping of protein/target to Protein and chemical:
               First, load all chemicals into the program.
               I did generate a manually checked list of all Targets that do not have a Uniprot ID if they are a protein or not. This information is load into the program.
               Next, load all Proteins.
               Then generate the cypher files to integrate the mapping between DrugBank protein and protein and DrugBank target and chemical. Also, cypher queries are generated to give the mapped node the additional labels like Target, Enzyme, Carrier, and Transporter. Moreover, the TSV file for the different mappings is generated.
               Next, the DrugBank proteins/targets are mapped to protein with the UniProt identifier. If it is not mapped and in the human, it is mapped to chemicals by name. After that, it is tried to be mapped to protein by name. All, mapped pairs are written into the TSV file.
               After this, I tried to Integrate the component 
relationship of DrugBank but because the protein which has multiple components have no UniProt identifier the information this information is not integrated.
               
Integrate the mapping of protein and target into the database with cypher-shell.
Prepare the relationships between 'compound-protein/target':
               First, take all  compound-protein/target (chemical) pairs where the relationship are in the human and have references and add them to a dictionary
               Then, go through all relationship pairs of the different relationship types and generate TSV files and cypher queries to integrate the information into the database. In the following, the pair information is written into the TSV file. If multiple edges with the same relationship type exist the information is combined and written into the TSV file.

Integrate the protein/target-compound relationship with cypher-shell.