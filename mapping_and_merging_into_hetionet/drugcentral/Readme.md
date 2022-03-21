There is a script to merge DrugCentral into PharMeBINet.

First, a mapping to protein takes place: not finished

Next, the DrugCentral DC_Products are mapped to Product.
    First, the TSV files for mapped and not mapped nodes are prepared. Also, the cypher query is generated and added to the cypher file.
    Next, the Product nodes are loaded and the information is written into a dictionary.
    Then, the DC_Products are loaded and mapped with NDC identifiers. The mapped and not mapped nodes are written into the TSV files.

Then, the DrugCentral DC_GOTerm are mapped to Biological Process (BP), Molecular Function (MF), and Cellular Component (CC).
    First, for every mapping, a TSV file is prepared.
    Then, the BP, CC, and MF data are loaded from Neo4j and their information is written into dictionaries.
    Next, the DC_GOTerms are loaded. Then based on their type (P[BP], C[CC], F[MF]) they are mapped to BP, MF, CC with GO identifier to GO identifier or alternative GO identifier. Then, the mapped pairs are written into the different TSV files.
    In the last step, the different cypher queries are generated and written into the cypher file.

The different mappings are merged into PharMeBINet with the Neo4j cypher-shell.

