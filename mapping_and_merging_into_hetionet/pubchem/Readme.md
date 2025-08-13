https://pubchem.ncbi.nlm.nih.gov/

Version: 

The script of PubChem is different from the others. It is because PubChem is too big. 

This has two parts: first, get the PubChem information from an API:
	First, generate a TSV file for the new PubChem chemical nodes and the additional cypher file with the cypher query.    
 Next, load all PharMeBINet chemicals with an identifier starting with "PubChem" and write them into a set.
 Load already downloaded API information from a TSV file and open it, or generate a new TSV file where the API information will be saved. Additionally, load all non-existing PubChem IDs and open them for further addition, or generate a new file.
	Now, for all PubChem IDs which were not in the already downloaded TSV files, are ask the api get an SDF file and transform it to a TSV file Format. It is written into the new node to generate the TSV and the API TSV file. If the API returns that it does not exist, write into the non-existent TSV file.
	
All nodes are integrated with Neo4j cypher-shell.

The second part:
The PubChem chemicals are mapped to chemical:
 First, the mapping TSV file is generated.
	Then, all chemicals with PubChem IDs are loaded and written into a dictionary.
 Next, load all PubChem nodes, combine the synonyms, prepare some PubChem properties to calculated-properties, and write this information into the TSV file.
 Last, generate a cypher file with a cypher query to merge the Information into the existing PharMeBINet node.
  
Last, the cypher query is executed with the Neo4j cypher shell.

License:https://www.ncbi.nlm.nih.gov/home/about/policies/