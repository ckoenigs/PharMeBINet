FoodON script contains multiple steps.
The FoodON foods are prepared and added:
    The first step is to generate for foods a new node TSV file, and the fitting cypher file is generated and add to the cypher file.
    In the following, the foods information are extracted and the xrefs are change and written into tsv file.
    Generate a edge cypher file.
    Then load all pairs with the edge type. For each new edge type generate a TSV file and add the cypher query to the cypher file.
    All pairs are written into the fitting TSV file.

Next mapped the FoodON anatomy to anatomy:
    First, the file for mapping anatomy as tsv is generated and the additional cypher query is added to the cypher file. 
    Second, all anatomies from PharMeBINet database are loaded into dictionaries.
    All FoodON Uberon nodes are loaded and mapped directly to anatomy. For the mapping the Uberon id where used. All mappings are written into the TSV file.

Next mapped the FoodON chebi ontology to chemical:
    First, load all chemicals and write information into a dictionary.
    Second, the file for mapping chebi ontology as tsv are generated and the additional cypher query is added to the cypher file. 
    All FoodON chebi ontology nodes are loaded and mapped to chemicals: 
        First, map with ChEBI id to chemical xrefs.
        Second, map name to name.
        Last, map name to synonyms.
    All mappings are written into the TSV file. 


The cypher shell integrates the addition and mappings.

Next, the relationships between the food and anatomy/chemicals are prepared:
    For each pair the following steps are executed:
        Load all pair in both direction and for each new edge type and direction generate a TSV file and the additonally cypher query.
        Then, write the pairs into the correct TSV file.

Last, the cypher shell integrates the edges into PharMeBINet database.