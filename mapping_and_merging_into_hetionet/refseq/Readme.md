The script starts with preparing the RefSeq RNA integration into PharMeBINet
    First, prepare the cypher file.
    Next, load all different kinds of RNA nodes from RefSeq and generate the different TSV files. Also, prepare the different cypher queries to give the nodes different labels.
    Additionally, all nodes id of the different types are written.
    Then, the TSV for RNA-RNA edges are prepared.
    All RNA-RNA edges are loaded from RefSeq and written into the TSV file.
    In the last step, the cypher file for the edge is generated and the additional RefSeq edge query is added.

Next, the RefSeq genes are mapped to the PharMeBINet genes:
    First, the TSV for the mappings is prepared and the cypher query is added to the cypher file.
    Then, the genes from PharMeBINet are loaded and the information is added to dictionaries.
    In the last step, the RefSeq genes are loaded and mapped with their xref Entrez id to the PharMeBINet gene identifier. All pairs are written into the TSV file.

Then, the Refseq CDS are mapped to protein:
    First, the TSV for the mappings is prepared and the cypher query is added to the cypher file.
    Then, the proteins from PharMeBINet are loaded and the information is added to dictionaries. Additionally, all gene-id to protein information is extracted and written into a dictionary.
    In the last step, the RefSeq CDS are loaded and mapped.
        The first mapping method is with the gene symbol to the protein id.
        The second method is the Uniprot identifier to the protein identifier.
    The mapping pairs are written into the TSV file.

The mappings and new nodes are integrated with the Neo4j cypher-shell and the cypher file.

In the following the integration of gene-RNA integration:
    First, generate the TSV file.
    Then, the Refseq gene-RNA pairs are loaded and written into the TSV file.
    In the last step, the cypher query is prepared and written into the existing cypher file.

In the following the integration of protein-RNA integration:
    First, generate the TSV file.
    Then, the Refseq gene-RNA pairs are loaded and written into a dictionary.
    Next, the information on the different edges of the same pair is combined and written into the TSV file
    In the last step, the cypher query is prepared and written into the existing cypher file.

In the last step, the edges are merged into PharMeBINet with Neo4j cypher-shell and cypher file.
