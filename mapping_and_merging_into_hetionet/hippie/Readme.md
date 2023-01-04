The script starts with mapping HIPPIE protein to protein:
    First, the TSV file is generated and opened, and the cypher file and query for the mapping are generated.
    Next, the protein information is loaded into dictionaries, and also a dictionary gene id to protein id is generated.
    Then the HIPPIE proteins are loaded and mapped:
        First, if the HIPPIE identifier is Entrez gene id it is mapped with the gene id to the protein. 
        Next, mapping is with the alternative UniProt id from HIPPIE protein to protein identifier.
    The mappings are written into the TSV file.

Next, the Neo4j cypher-shell integrates the mapping.

Next, the interaction edges are merged.
    First, existing interaction edges are loaded with resource, method, and publication information.
    Then, load the Hippie pairs and check if they exist (directed) or not. All information is gathered in dictionaries. 
    In the last step, the tsv files for mapped and new edges are generated. Additionally, a cypher file with cypher queries to update information and create new interactions is prepared. 
        Then, all the new interactions are prepared and written into the TSV file.
        Next, for the mapped interaction the information is combined and written into the TSV file.

In the last step, the Neo4j cypher-shell integrates the edge information into PharMeBINet.