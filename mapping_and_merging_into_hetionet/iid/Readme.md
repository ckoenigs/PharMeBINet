The script first mapped the IID protein to protein and then integrate the protein-protein interaction.

The program map the IID protein to protein:
               First, generate the mapping TSV file, the cypher file, and the cypher query to integrate the information into the database.
               Then, the IID proteins are mapped to the Uniprot identifier and alternative UniProt identifier of the protein.

Then the cypher-shell integrates the mapping.

Next, the preparation integrates the protein-protein interactions.
               First, the CC information is loaded into a dictionary from name to GO identifier.
               Then, load all protein-interaction pairs which are experimentally based. If a cellular component is part of the interaction relationship then a set for this pair is generated and the pair relationship information is part of a dictionary with a list of interaction relationships. The same is done for self-loops. The information of the interaction to diseases or drugs is ignored because they are only the connection if both proteins appear to be associates with the same drug/disease.
               In the last step, the different TSV files for protein-interaction information, and interaction to CC is being generated. The same goes for the cypher queries to integrate the relationships. The interaction edge is a meta node because it can be connected with more than two nodes. All the information is written into the TSV files. If a protein pair contains multiple interactions then the information is combined into one node.        

The last step is to integrate the Interaction nodes and the fitting relationships between protein interaction and interaction and CC with the cypher shell.