# IID

http://iid.ophid.utoronto.ca/

Version: 2021-05

First, the program downloads the file from Integrated Interactions Database (IID) version 2021-05.
Next, the cypher file and the cypher queries are generated to integrate all the information.
Then it runs through the file to generate for the protein nodes an own tsv file. 
Also for the relationships is a new file is generated because it handles empty values differently and all are now empty strings. 
Additionally, only by properties where still exists only 0 and 1 the 1's are changed into true. Additionally, now exists direction information and they are considered if they are only in one direction. Else they have the additionally property bidirected=true.

As the last step, the data are integrated into Neo4j with the cyher-shell and the cypher file.

License: free to use for academic purposes