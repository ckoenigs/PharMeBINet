The script starts with the mapping program.

The UBERON anatomy mapping to anatomy:
    First, generate two TSV files one for mapping and one for new nodes. Additionally, a cypher file is generated to integrate the information into PharMeBINet and queries to add is-a and part of edges.
    Next, check for each UBERON node that has an edge with a taxon if they have a human connection and save the information in a dictionary.
    Then, load all anatomy nodes into dictionaries.
    In the following, all sub-nodes of the node "anatomical structure" (UBERON:0000061) which are human or have no taxon or the xrefs are from human resources. These are only the nodes that are connected with part-of or is-a. Then the nodes that get through the filters are mapped to anatomy with uberon ID and written into the TSV file. The not mapped are written into the other TSV file.


Next, the Neo4j cypher shell integrates the mappings with the use of the cypher file.