This program integrates MONDO to disease.

The program merges the MONDO diseases as diseases into the database.
    First, all non-human diseases are extracted and added to a set.
    Next, all properties are loaded off the MONDO disease and are used for the TSV files for new nodes, and is_a relationships between the MONDO disease nodes.
    Then, load the MONDO disease, filter the animal disease out, update the xrefs, and write information into the TSV file.
    Next, the cypher query integrates the new disease nodes and writes the edge cypher query in another cypher file.
    Last, load all edge pairs and write the information into the edge TSV file.

Then, the cypher file is executed with Neo4j cypher-shell and add disease nodes.

Last, the relationships are added between diseases with the Neo4j cypher-shell and the edge cypher file.