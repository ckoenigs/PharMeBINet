For mapping and merging ADReCS a bash script is executed.

First, the ADReCS drugs are mapped to Chemical:
    First, load all chemical information into different dictionaries for the different mappings. Additionally, a dictionary is generated from chemicals to their salt ids.
    Next, the mapping TSV file is generated and the additional cypher query is generated and written in a new cypher file.
    In the following, it runs through all ADReSC drugs and is mapped:
        First, mapping is with a manually generated list.
        Next, in case it has a drugbank id and if the drugbank id is in the dictionary with salts then an intersection between the name mapping and the salt ids is generated (a lot of salts are connected to the main drug and not to the real salts). If the intersection is greater 0 then it is mapped else if the drugbank is in chemical then it is mapped with only the drugbank id.
        In the following, the mapping is between the ADReCS name and the name/synonyms of chemicals.
        Then, it is mapped with the PubChem id, next to the kegg id, and then with the TTD id to the different xrefs of the chemical nodes.
        The last mapping method is the mapping between the mesh id to the identifier of the chemicals.
    For each mapping, the mapping pair is written into the TSV file.

Next, the ADReCS ADRs are mapped to SideEffects(SEs):
    First, load all SEs information into different dictionaries for the different mappings. 
    Next, the mapping, new, and connection between the new nodes and the existing ADR of ADReCS TSV files are generated and the additional cypher queries are generated and written into the existing cypher file.
    In the following, it runs through all ADReSC ADRs and is mapped or written for a new generation:
        First, mapping is with a name to name/synonyms of the SEs nodes.
        Next, with UMLS a UMLS cui is got for the name. And with the umls cui is mapped to the identifier of SE.
        Then, the last mapping method is with the MedDRA id to the MedDRA id of the xrefs of SE.
        The ADR nodes which have at least one UMLS cui and are not mapped are added to a dictionary and the information is combined if more than one map to the same UMLS cui. The pairs are written into the connection file.
    For each mapping, the mapping pair is written into the TSV file.
    Additionally, for each new UMLS cui a new entry is generated in the new TSV file.


The cypher file for the nodes is executed with the cypher-shell tool.

Next, the edge information is prepared.
    First, a new cypher file is generated.
    Then, the edge TSV file is generated.
    Next, the chemical-SE pairs over ADReCS are loaded with the relationship information. Only edges are allowed where a FAERS frequency exists.
    All pairs are written into a dictionary with a list of edge information for the same pair.
    Then, for each pair are the edge information combined and written into the TSV file.
    In the last step, the cypher query is generated and added to the cypher file.

In the last step, the last cypher file is used to integrate the edges into Neo4j.


