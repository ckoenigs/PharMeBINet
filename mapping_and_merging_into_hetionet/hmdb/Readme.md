The script to merge HMDB information into the database contains two scripts:
First script:
First, the HMDB metabolite, filter after not predicted one, the xrefs are prepared and written into a tsv file and the cypher query to integrate the data.

Next, the HMDB GO terms are mapped to Biological Process (BP), Molecular Function (MF), Cellular Component (CC):
    First, the BP, CC, and MF information are loaded.
    The GO Terms in HMDB have GO identifiers so that they can map to BP, CC, MF identifier, and alternative identifier.
    All mapping pairs are written into tsv files. Additionally, cypher queries are generated and added to the cypher file.

Then the HMDB proteins are mapped:
    Frist the protein information from pharMeBINet ard asked.
    The proteins from HMDB have UniProt identifier information which is used to map to the protein identifier.
    All mapping pairs are written into a tsv file. Additionally, a cypher query is generated and added to the cypher file.

The first mappings are integrated into the database with neo4j cypher-shell.

Second script:
First, the HMDB pathways are mapped:
    First, the pathways from PharMeBINet are loaded.
    The HMDB pathways are mapped with two mapping methods. The first is the SMPDB identifier and the other is name-based.
    The mapped pairs are written into a tsv file. Additionally, a cypher query and cypher file are generated.

Next, connections between compound and metabolite are generated:
    First, load all compound information.
    Then the metabolite information is asked and used for mapping. One is the InChIKey and the other a combination of the DrugBank identifier and name mapping.
    All pairs are written into a TSV file and a cypher query is generated and added to the cypher file.

The HMDB disease is mapped to disease and symptom:
    First, the disease and symptom information are written into dictionaries.
    Then the TSV files are prepared for the different mapping pairs and the fitting cypher queries are generated and added to the cypher file.
    The HMDB diseases are mapped to diseases with name to name, name to synonyms, and with OMIM ids.
    For the mapping to symptom name to name and name to synonym mapping were used.
    All mapping pairs are written in the fitting TSV files.

The data are merged into the database with the Neo4j cypher shell.

Next, the preparation of all edges without information is prepared (protein-pathway/BP/CC/MF and) metabolite-pathway:
    First, the cypher file is generated.
    For each combination the same steps take place:
        First, a TSV file is prepared for existing pairs and not existing pairs.
        The existing pairs in the database are loaded into dictionaries.
        Then, all existing and not existing pairs of HMDB are written in the different TSV files. 
        Then the cypher queries are generated and written into the cypher file.
    
    Currently only the metabolite-pathway edges are integrated because they come from KEGG and METACYC (https://hmdb.ca/sources). The edges to GO are not used because they are from GO (already included) and automatic generated. The edge protein-pathway are from KEGG and UniProt, however, the UniProt edges are Semiautomatic geenerated.

In the last program, prepare the edges from HMDB which includes information (metabolite-protein/disease):
    Both edges are not in the database. So for each combination, only the edges with reference information are taken.
    The reference information is prepared into a list of PubMed identifiers, URLs, and reference texts.
    Then the TSV file are prepared and the information is written into them.
    In the last step, the cypher queries are generated and added to the cypher file.

The last step is to integrate the different edge information into the database with the Neo4j cypher shell.