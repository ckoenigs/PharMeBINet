The first program maps bindingDB polymer to protein:
    First, it generates an empty cypher file.
    In the following, it loads all proteins and writes them into dictionaries.
    Next, it generates the mapping TSV file and adds a cypher query to the newly generated cypher file.
    Then, load all bindingDB polymers and map them to proteins:
        First, the polymer UniProt ID is mapped to the protein identifier.
        Then, the polymer UniProt ID is mapped to the protein alternative identifiers.
        Next, the polymer UniProt ID in the isoform is split and mapped to the protein identifier.
        The following mapping is between the polymer display name and the protein name.
        The last mapping is polymer synonyms to protein synonyms.
    All mapping pairs are written into the TSV file.

The next program maps bindingDB monomer to chemical:
    First, load all manually executed InChiKey to PubChem id (https://pubchem.ncbi.nlm.nih.gov/idexchange/idexchange.cgi) information into a dictionary.
    Next, load existing chemical information into dictionaries.
    Then, generate mapping TSV file and additional cypher query and add to cypher file.
    In the following, the new TSV file is generated and the additional cypher query is added to the cypher file.
    Next, the bindingDB monomer nodes are loaded and mapped:
        The first mapping method is with monomer inchikey to chemical inchikey.
        The following mapping is with monomer SMILES to chemical SMILES.
        Next, the monomer name is mapped to the chemical name/synonym.
        Then, the monomer synonym chembl id is mapped to chemical xref chembl id (some have also the first part of the inchikey equal).
        In the following, monomer synonym is mapped to chemical name/synonym (some have also the first part of the inchikey equal).
        Next, the monomer bindingDB id is mapped to the chemical xref bindingDB id.
    All mappings are written into the mapping TSV file.
    The not-mapped nodes with an InChiKey which is in the dictionary to PubChem ID are added to the new TSV file.
    The not-generated new nodes that include an InChiKey are written into a tsv file which can be executed in https://pubchem.ncbi.nlm.nih.gov/idexchange/idexchange.cgi

The mapping is integrated into PharMeBINet with Neo4j cypher-shell and the cypher file.

Next, the bindingDB complex nodes and edges are merged into PharMeBINet:
    First, a cypher file is generated.
    Then, prepare integration TSV file and add cypher query to cypher file to add complex nodes.
    Next, write all complex nodes into the TSV file if it is connected to PharMeBINet chemical or protein.
    In the following, for chemical and protein, the following steps are executed:
        First, generate a TSV file and add a cypher query to the cypher file for the edge between the complex and the node type.
        Load the pairs and prepare their information and write them into the TSV file.

Then the complex and the complex edges are integrated into PharMeBINet with Neo4j cypher-shell and the cypher file.

The last program is to prepare the bindingDB node-edge ERS (EnzymeReactantSet) and the fitting edges:
    First, a cypher file is generated.
    Then, load all polymer-protein, monomer-chemical, and complex-complex pairs into dictionaries. Prepare an entry ID assay description dictionary, a dictionary from entry-id to different references, and a dictionary entry-id to reaction information.
    Next, prepare the TSV file for the ERS.
    All ERS are loaded, but all ERS which have in inhibitor a monomer that is not connected to chemical or enzyme not connected to chemical/protein/complex or substrate not connected to chemical/protein/complex or has no reference is not added. In the one that accepts these conditions, the different information is combined and written into the TSV file.
    The edge information is written into dictionaries.
    Next, the cypher query for integrating the ERS into PharMeBINet is prepared and added to the cypher file.
    In the last step, for each edge type, the following steps are executed:
        A TSV file is prepared.
        Then, each edge is prepared and written into the TSV file.
        In the end, the cypher query is prepared and added to the cypher file.

In the last step, the edge and edge nodes are integrated with the Neo4j cypher-shell and the cypher file.