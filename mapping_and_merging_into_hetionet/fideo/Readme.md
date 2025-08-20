The FIDEO script contains multiple steps.

First, the FIDEO food is mapped to food:
    First, the file for mapping food as tsv is generated, and the additional Cypher query is added to the generated Cypher file. 
    Second, all foods from the PharMeBINet database are loaded into dictionaries.
    Next, all FIDEO food nodes (nodes with the identifier FOODON) are loaded and mapped by their FOODON IDs. All mapping pairs are written into the TSV file.

Second, the FIDEO chemicals are mapped to chemicals:
    First, load all chemicals from PharMeBINet and write the information into dictionaries. Additionally, get all ChEBI-chemical mappings into a dictionary.
    Next, generate the mapping TSV file and write the mapping query into the existing cypher file.
    Then, map the FIDEO chemicals (ChEBI or DRON identifier) to chemical:
        First, map with the ChEBI ID over the Chebi mapping to the chemical.
        Then, a manual mapping is executed for the chemical.
        Last, a name mapping from FIDEO to a chemical is executed.
    All mapping pairs are written into the TSV file.
    Additionally, the reference FIDEO nodes are mapped to chemicals with DrugBank ID and written into the same TSV file.


The cypher shell integrates the mappings.

Next, the food-chemical interactions are merged to PharMeBINet:
    First, load all FIDEO nodes that are connected to the Food interaction node (FIDEO:00000006).
    Next, get for the fideo nodes the reference information.
    Then, load the mapping from the reference nodes to the chemical into a dictionary.
    Next, generate an adding TSV file and the cypher file with the cypher query.
    Then, load all food-chemical pairs from Fideo. The edges need to have reference information and be a food-interaction edge node.
        Additionally, if the chemical name is in the food interaction text, then the pair is used.
        Otherwise, check for the reference mapping chemical nodes and use them for the pair.
        If neither is clear, then use the formal pair again.
        For all pairs in the compound food description from DrugBank is used to find an interaction text is found and written to the edge.


Last, the cypher shell integrates the edges into the PharMeBINet database.