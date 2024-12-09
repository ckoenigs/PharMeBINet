The UBERON anatomies are added as anatomy:
    First, generate a TSV files for new nodes. Additionally, a cypher file is generated to integrate the nodes into PharMeBINet and queries to add is-a and part of edges.
    Next, check for each UBERON node that has an edge with a taxon if they have a human connection and save the information in a dictionary.
    Then, load all anatomy nodes into dictionaries.
    In the following, all sub-nodes of the node "anatomical structure" (UBERON:0000061) and disconnected anatomical group (UBERON:0034923) which are human or have no taxon or the xrefs are from human resources. Nodes with xrefs from other taxonomies are ignored if not a human xref is included. These are only the nodes that are connected with part-of or is-a. the nodes are written into the TSV file.


Next, the Neo4j cypher shell integrates the mappings with the use of the cypher file.