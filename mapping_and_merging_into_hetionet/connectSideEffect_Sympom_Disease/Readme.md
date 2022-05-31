This script generates relationships between the different kinds of phenotypes. This includes SE-symptom, SE-disease, symptom-disease, and SE-phenotype.

The SE-symptom edges use:
	Name mapping
	Mapping with xref UMLS cui to SE identifier
	Mapping Mesh to UMLS CUI and try to map to SE identifier

The SE-disease edges use:
	Disease external identifier  from UMLS are mapped to SE identifier
	Disease external identifier  from MedDRA is mapped to SE external identifier
	Name mapping
	Synonym of disease to SE name
	Disease name to UMLS to get UMLS CUI and map to SE identifier

The symptom-disease edges use:
	Disease UMLS cui to symptom xref UMLS cui
	Disease external identifier  from MESH are mapped to SE identifier
	Name mapping

The SE-phenotype edge use as mapping:
	External identifier UMLS CUI from phenotype to SE identifier
	External identifier MedDRA ID from phenotype to SE external identifier
	Name mapping
	Synonyms of phenotype to SE name
	Phenotype name to UMLS to get UMLS CUI and map to SE identifier
              
All the mapping pairs are written into a TSV file and for each label pair, a cypher query is generated and wrote into a cypher file.
In the end, the information is integrated into the database with the cypher shell.