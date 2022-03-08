This program integrates MONDO to disease and changes the identifier from DOID to MONDO.

First, the program tries to map the MONDO disease to the disease in the database.
               First, all properties are loaded off the MONDO disease and are used for the TSV files for new nodes, mapped nodes, and is_a relationships between the MONDO disease nodes.
               Then, load the MONDO disease and prepare the different dictionaries for the mapping.
               The first mapping method is based on the DOID to the external reference DOID from MONDO. Next is the mapping of the alternative DOID to MONDO external references.
               Now, all mapped nodes are written into a TSV file with combined information of MONDO and DO. If multiple diseases are mapped to one MONDO disease only one pair is added to the TSV file and the others are added to the merge script. The not mapped are written into their TSV file.
               In the last step, all is_a relationships of MONDO are extracted and wrote into another TSV file.

Next, change the existing node identifier to the MONDO identifier and add new information. Also, new nodes are integrated. All of this is done by the cypher shell.

Disease nodes where more than one node mapped to MOND the other are merged into the one node with the merge script.

In the last step, the disease nodes that did not map to MONDO are removed with the cypher-shell and the cypher file.