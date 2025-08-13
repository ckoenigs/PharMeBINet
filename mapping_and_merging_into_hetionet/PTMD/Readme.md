First, map the PTMD disease to disease, symptom, and phenotype:
    First, load all PharMeBINet disease, symptom, and phenotype information into dictionaries.
	Next, prepare the mapping TSV file and the cypher file with the mapping query.
	Last, load all PTMD diseases and map them:
		First, mapping with the name to the disease name.
		Then; name to symptom name.
		Next, with name to phenotype name.
		Then, the manual mappings are executed.
		Next, use UMLS with the name and map it to the disease umls ID.
		In the following, the name is mapped to the disease synonym.
		Then, the name mapped UMLS id is mapped to symptom UMLScui.
		Next, the name is mapped to the symptoms synonym.
		Last, the UMLS cui from UMLS is mapped to the phenotype UMLS cui.
	All mapping pairs are written into the TSV file.
	
Next, map the PTMD proteins to proteins:
    First, load all PharMeBINet protein information into dictionaries and also the gene-protein connection information.
	Next, prepare the mapping TSV file and open the existing cypher file and write the mapping query.
	Last, load all proteins from the human and map it:
		First, mapping with UniProt identifier.
		Last, it is mapped with an alternative UniProt ID.
	All mapping pairs are written into the TSV file.
	
Then the mappings are integrated into PharMeBINet with Neo4j cypher shell.

Next, the PTMD PTMs are added to PharMeBINet:
	First, generate a TSV file for PTMs, and generate a cypher file with the additional cypher query.
	Last, load all PTMD PTMs that are connected to mapped PTMD proteins:
		First, the identifier is generated based on the UniProt ID, position, residue, and ptm type.
		All PTM which contains all information for the identifier are written into the TSV file.
		
Then the mappings and add of PTMs are integrated into PharMeBINet with Neo4j cypher shell.

Next, the PTMD PTM-disease edges are added:
	First, generate cypher file.
	Then, load all tuples with collect relationship information. Because all data sources ActiveDriverDB, BioMuta and PhosphoSitePlus seems to be high quality data all edges are used)
		For each new edge type (regulation) generate a TSV file and add the cypher query to the cypher file.
		Gather all information in a dictionary and in the end combine the information and write them to the different SV files.
		

Last, the PTMD PTM-protein edges are added:
	For only the has edge type the following steps are executed (the involves edge is not sure where this information come from):
		First, prepare the new add edge file as TSV.
		Then, load all tuples and write them into the TSV files.
		Last, write the cypher query in the existing cypher file.
		
Last, add the PTMD edges into PharMeBINet with the Neo4j cypher shell.