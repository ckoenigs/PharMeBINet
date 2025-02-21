Cl script contains multiple steps.
The CL cell types are prepared and added:
               The first step is to generate for cell type a new node TSV file, and the fitting cypher file is generated and add to the cypher file.
               In the following, the Cell types which are human (human_subset in subsets) information are extracted and the xrefs are change and written into tsv file.
                Also, the is_a relationships of CL are extracted and wrote into TSV files. Additionally, cypher queries for integrate these relationships are generated and add to the cypher file.

Next mapped the CL anatomy to anatomy:
    First, the file for mapping anatomy as tsv are generated and the additional cypher query is added to the cypher file. 
    Second, all anatomies from PharMeBINet database are loaded into dictionaries.
    All CL unberon nodes are loaded and mapped directly to anatomy. For the mapping the Uberon id where used. All mappings are written into the TSV file.

Next mapped the CL BP, CC, MF to BP, CC, MF:
    For each  of the CL BP, CC,and MF the following steps are executed:
        First, all nodes from PharMeBINet with this type are loaded into dictionaries.
        Second, the file for mapping anatomy as tsv are generated and the additional cypher query is added to the cypher file. 
        All CL nodes are loaded and mapped directly to the PharMeBINet nodes. For the mapping the GO id where used. TO the identifier or the alternative identiver. All mappings are written into the TSV file. 


The cypher shell integrates the addition and mappings.

Next, the relationships between the Cell type and anatomy/BP/CC/MF are prepared:
    For each pair the following steps are executed:
        Load all pair in both direction and for each new edge type and direction generate a TSV file and the additonally cypher query.
        Then, write the pairs into the correct TSV file.

Last, the cypher shell integrates the edges into PharMeBINet database.