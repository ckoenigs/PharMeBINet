The script starts with the mapping program.

The EFO disease mapping to disease:
    First, load all diseases from PharMeBINet and write the information into the dictionaries.
    Then, prepare the mapping TSV file and create the cypher file with the additional cypher query to map the data.
    Next, the EFO entry EFO:0000408 is loaded and mapped to the disease with MONDO.
    Then all nodes under disease are loaded and mapped:
        First, mapped the EFO mondo identifier to the disease identifier.
        Second, map with EFO xref mondo id to disease identifier.
        Next, mapping is with EFO xref Orphanet id to disease xref Orphanet id.
        The last mapping is with EFO name to disease name/synonyms.
    All mapping pairs are written into the TSV file.

The EFO drug mapping is not used because less than 10 drugs map and no other mappings exist!

Next, the Neo4j cypher shell integrates the mappings with the use of the cypher file.

Then, the is-a edges of EFO are merged to the PharMeBINet is-a relationships of disease:
    First, all is-a pairs of PharMeBINet are loaded and written into a dictionary.
    The two TSV files are generated one for the mapped edges and one for the new edge. Additionally, the cypher file is generated where two cypher queries are added to update the existing edges and create new ones.
    Last, the edge pairs of EFO are loaded and are written into either mapped or in the new TSV file.

In the last step, the edges are updated or created with the cypher file and the Neo4j cypher-shell.

