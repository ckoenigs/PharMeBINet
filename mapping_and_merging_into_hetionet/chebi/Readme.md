The ChEBI script contains multiple steps.

First, map the ChEBI chemicals to chemical:
    First, load all chemical information from PharMeBINet into dictionaries. Additionally, generate a dictionary from chemical IDs to their salt forms.
    Next, generate the mapping TSV file and the cypher file with the additional cypher query.
    Then, the ChEBI nodes are loaded and mapped to chemical:
        The first mapping is with InChIKey from ChEBI to PharMeBINet.
        The next mapping is the name and first part of the inchikey to the chemical with the same name and additional inchikey.
        Then, name mapping.
        Then, name to synonyms of chemical and the first part of the inchikey needs to be mapped.
        In the following, the name is mapped to synonyms, but only for Drugbank or Mesh chemicals; the other are not good.
        Next, a manual mapping is used.
        Then, the DrugBank of the ChEBI node is used to map to chemicals, but the number of words is equal to the chemical name or length 1. Otherwise, the salts of the chemicals are checked. This requires that at least a part of the name is equal to the length of the name are equal.
        Last, the ChEBI ID is mapped to the chemical xrefs.
    All mapping pairs are written into the TSV file.

The cypher shell integrates the mappings.

Next, the relationships between the ChEBI nodes are merged to PharMeBINet chemicals:
    First, generate a cypher file for the edges.
    Then, load all ChEBI edges, and for each new type a TSV file and a cypher query are added. The pairs are written in the TSV files.

Last, the cypher shell integrates the edges into the PharMeBINet database.