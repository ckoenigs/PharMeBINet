ATC is mapped to Pharmacological Class (PC) and Chemical. 
First, the ATC nodes are mapped to the Chemical which has an ATC code. The others are mapped to PC with name mapping. But if multiple mapping for name mapping is not allowed for PC so only the hierarchical lowest ATC code map. 
The nodes that are not mapped will generate new PC nodes. All mappings and the new node get their own tsv file. 
Additionally, a cypher file is generated with the different integration of mapping information and the new PC nodes. All are integrated with the cypher-shell tool.
