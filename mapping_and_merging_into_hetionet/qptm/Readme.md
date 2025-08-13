First, map the qPTM proteins to proteins:
    First, load all PharMeBINet protein information into dictionaries and also the gene-protein connection information.
	Next, prepare the mapping TSV file and the cypher file with the mapping query.
	Last, load all proteins from the human and map it:
		First, mapping with UniProt identifier.
		Then, with the gene symbol to the gene and from there to the PharMeBINet protein.
		Last, it is mapped with an alternative UniProt ID.
	All mapping pairs are written into the TSV file.
	
Then the mappings are integrated into PharMeBINet with Neo4j cypher shell.

Next, the qPTM PTMs are mapped to PTM:
	First, the existing PTMs are loaded into dictionaries.
	Next, generate TSV files for mapping and add of PTMs, and generate a cypher file with the additional cypher queries.
	Last, load all qPTM PTMs that are connected to mapped qPTM proteins (all connections are validated with PubMed IDs) and map it:
		First, the identifier is generated based on the UniProt ID, position, residue, and ptm type.
		This is mapped by identifier to the existing PTMs. These mappings are written into the mapping file.
		The not-mapped PTMs are written into the file with the new PTMs.
		
Then the mappings and add of PTMs are integrated into PharMeBINet with Neo4j cypher shell.

Last, the qPTM PTM-protein edges are merged and added:
	First, load existing edges from PharMeBINet into a dictionary.
	Next, prepare the merging and new add edge files as TSV and generate a cypher file with the additional cypher queries.
	Last, the qPTM tuples with edge information are loaded, and the PubMed information a gathered in a set.
		The tuple is checked if it is already in PharMeBINet or not and depending on this the information is written into different TSV files.
		
Last, add and merge the qPTM edges into PharMeBINet with the Neo4j cypher shell.