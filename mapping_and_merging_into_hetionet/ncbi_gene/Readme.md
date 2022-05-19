The script first prepared the mapping and the new node files and then integrates the information into the database.

The program first prepares the TSV file for all node information. Then it generates the cypher query to merge the NCBI gene nodes into the database. If the node exists already then add only information else generate a new gene node.
Also, all gene nodes which do not map to the NCBI gene are removed with a query that is added to the cypher file.
The name of the NCBI gene is prepared depend on which information exists.
The genes are mapped on their identifier. All mapped nodes and not mapped nodes are added to the TSV file.

Next, the information is integrated with the cypher-shell into the database.

