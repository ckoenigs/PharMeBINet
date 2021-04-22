With the pathway script, the pathways are completely replaced and additional pathway-gene relationships are generated.
The program first generates the node and edge TSV files and then load all human disease in a dictionary.
Next, get all properties of the pathway nodes (of the two sources) and add them to the header.
The pathways are grouped by name. The genes of a pathway are written into a dictionary pair.
Then the TSV file for the pathways gets the header. Then for each name, if only one pathway has this name it is written into the TSV file. The name with multiple pathways the information is combined and then is written into the TSV file. Additionally, a dictionary is written from the old pathway to the merged identifier.
In the last step, all pathway-gene pairs are add written into the TSV file but with the merged identifier if this node was merged. Additionally, cypher queries are added to the cypher file to integrate the pathway nodes and the pathway-gene edges into the database.
The last step of the script is, the cypher-shell integrates the node and edges into the database.
