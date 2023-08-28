ATC is mapped to Pharmacological Class (PC) and Chemical. 
    First load PCs and chemicals and write the information into dictionaries.
    Then, prepare the different TSV files for mapping (PC and chemical) and new node creation (PC). Also, the fitting cypher queries are added to the newly generated cypher file. Additionally, queries were added to create edges between the nodes. 
    Next, the ATC nodes are mapped to the PC with name mapping and written into a dictionary.  If not they are added to the newly generated node and directly added to the TSV file. Additionally, the not mapped atc are mapped to chemicals with ATC code to generate a connection between PC and chemical. They are written into the TSV file.
    Next, the mapped to PC are prepared for TSV writing. If multiple ATCs map to the same PC only the longest is added to the mapped TSV and the others are added to the newly generated PC file. If only one map it is directly written into the mapping TSV file. Also, these nodes are checked if they can map to chemical and are written into the TSV file if so.

In the last step, the script executes the cypher queries of the cypher file with Neo4j cypher-shell.

