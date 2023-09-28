The script starts with mapping the miRBase gene to the gene:
    First, prepare the mapping TSV file and the cypher file. Also, a mapping query is added to the cypher file.
    Next, load all genes and write the information into dictionaries.
    Last, all miRBase genes that are connected to pre-miRNA and are from humans are loaded and mapped:
        First, mapping is with the Entrez ID to the gene identifier.
        The second mapping is with HGNC to the HGNC IDs from the gene xrefs.
    All mapping pairs are written into the TSV file.

The next program is mapping miRBase pre-miRNA and the miRNA to primary transcript and miRNA (of RNA):
    First, load the miRNA and Primary Transcript and write their information into dictionaries.
    Next, the TSV files for the mappings are prepared and the cypher queries are added to the cypher file for pre-miRNA and miRNA of miRBase.
    Then, for each miRNA and pre-miRNA they were loaded if they were human, and then they were mapped to miRNA or Primary Transcript:
        They are mapped with the miRBase accession to the miRBase xrefs of miRNA/Primary Transcript.
    All, mapping pairs were written into the different TSV files.

Next, the mappings are integrated into Neo4j with the Neo4j cypher-shell and the cypher file.

Last, the programm merge miRBase gene-pre-miRNA and pre-miRNA-miRNA:
    First, the gene-pre-miRNA is prepared:
        First, load all existing pairs and write the information into a dictionary.
        Next, the TSV file is prepared and all pairs that are connected through miRBase are loaded and mapped.
        All, mapping pairs and new edges are written into the TSV file.
    Next, the same steps are executed for pre-miRNA and miRNA.
    Last the cypher file is generated and cypher queries are added.
 
