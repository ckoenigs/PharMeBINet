Hetionet merge contains two scripts.

The first script mapped a lot of nodes.

First, map Hetionet genes to genes:
    First, load PharMeBINet nodes into a dictionary for the resource.
    They generate a TSV file and a cypher file with an additional mapping cypher query.
    Then load Hetionet genes and map to genes with the identifier.
    All pairs are written into the TSV file.

Then, Hetionet diseases are mapped disease:
    First, generate a mapping TSV file.
    Then, generate the cypher query and add it to the cypher file.
    Next, load all PharMeBINet diseases and generate different dictionaries with their information.
    Then, the Hetionet diseases are loaded and mapped:
        First, map the identifier to the disease xrefs DO id.
        Then, the name is to name of the disease mapped.
    All mapping pairs are written into the TSV file.

Next, the Hetionet anatomies are mapped to anatomies:
    First, generate a mapping TSV file and add a mapping cypher query to the cypher file.
    Next, load PharMeBINet anatomies into a dictionary.
    Then, load all Hetionet anatomies and map them with the identifier to the identifier. All mappings are written into the TSV file.

Then, the Hetionet symptoms are added to PharMeBINet:
    First, generate a TSV file for the new nodes.
    Then, prepare the cypher queries with the properties of the nodes and add the cypher query to the cypher file.
    Last, all node IDs are written into the TSV file.


Next, the Neo4j cypher shell integrates the mappings with the use of the cypher file.

Then the edges disease-symptom, disease-gene, disease-anatomy, disease-disease, anatomy-gene, and gene-gene are prepared:
    First, a relationship cypher file is generated.
    Then, for each edge pair and type the following steps are executed:
    First, load the edge properties, prepare the cypher query, and add it to the cypher file.
    Then, generate the TSV file for the edge pairs.
    Next, load all pairs with their relationship information and add them to a dictionary. Then, combine the information and write it into the TSV file.

In the last step of the first script, add the edges to PharMeBINet with Neo4j cypher-shell and the cypher file.

The second script focuses on compounds.

First, the Hetionet compounds are mapped to PharMeBINet compounds:
    First, generate a mapping TSV file.
    Then, generate the cypher file with the mapping cypher query.
    Next, load PharMeBINet compound information into dictionaries.
    Then, load Hetionet compounds and map them:
        First, map with identifier to identifier.
        Then, InChIKey to InChIKey.
        Next, map the identifier to the PharMeBINet alternative identifier.
        Last, map with name to name.
    All mapping pairs are written into the TSV file.

The cypher-shell integrated the compound mapping into PharMeBINet.

Last is the preparation of the compound-disease and compound-gene edges from Hetionet.
    First, generate a cypher file:
    Then for each label pair and edge type, the following steps are executed:
    First, load the relationship properties and prepare a cypher query and add it to the cypher file.
    Next, generate a TSV file for the edge pairs.
    Then, load the pairs and write the information into a dictionary and then combine the information to write them into the TSV file.

Last, the compound edges are added to PharMeBINet with the cypher file and the cypher-shell.