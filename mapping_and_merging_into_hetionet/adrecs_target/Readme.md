For mapping and merging ADReCS-Target a bash script is executed.

First, the ADReCS drugs are mapped to Chemical:
    First, load all chemical information into different dictionaries for the different mappings. 
    Next, the mapping TSV file is generated and the additional cypher query is generated and written in a new cypher file.
    In the following, it runs through all ADReCS-Target drugs and is mapped:
        The first mapping method is ADReCS-Taget drug DrugBank ID to chemical identifiers.
        The next mapping is with drug name to chemical name/synonym.
    For each mapping, the mapping pair is written into the TSV file.

Then, the ADReCS genes and proteins are mapped to genes/proteins:
    For, gene and protein mapping the following steps are executed for each:
        First, load all gene/protein information into different dictionaries for the different mappings.
        Next, the mapping TSV file is generated and the additional cypher query is generated and written in the cypher file.
        In the following, it runs through all ADReCS-Target genes/proteins and is mapped:
            First, mapping is with the gene id/UniProt id to the fitting identifier of gene/protein.
            Next, the gene-id/uniprot id is mapped to the alternative IDs of gene/protein.
        For each mapping, the mapping pair is written into the TSV file.

In the following, the ADReCS variants are mapped to variant:
    First, load all variant information into different dictionaries for the different mappings.
    Next, the mapping and new node TSV files are generated and the additional cypher queries are generated and written in the cypher file.
    In the following, it runs through all ADReCS-Target variants and is mapped:
        First, mapping of ADReCS-Target variant ID to a variant identifier.
        Next, is ADReCS-Target variant ID to variant name/synonym.
        All not mapped but with an rs ID are written into the new TSV file.
    For each mapping, the mapping pair is written into the TSV file.

Next, the ADReCS ADRs are mapped to SideEffects(SEs):
    First, load all SE information into different dictionaries for the different mappings. 
    Next, the mapping, new, and connection between the new nodes and the existing ADR of ADReCS TSV files are generated and the additional cypher queries are generated and written into the existing cypher file.
    In the following, it runs through all ADReSC ADRs and is mapped or written for a new generation:
        First, the mapping is between the ADR name and to SE name/synonym.
        Next, with the use of UMLS the ADR name is mapped to UMLS Cui and this is mapped to the SE identifier.
        The ones that got a UMLS Cui from UMLS but could not mapped are added to the new TSV file.
    For each mapping, the mapping pair is written into the TSV file.


The cypher file for the nodes is executed with the cypher-shell tool.



