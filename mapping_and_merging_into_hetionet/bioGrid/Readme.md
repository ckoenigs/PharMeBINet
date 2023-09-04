The script first removes the existing cypher file.

The first program maps bioGRID gene to gene:
    First, it loads all genes and writes them into dictionaries.
    Next, it generates the mapping TSV file and adds a cypher query to the newly generated cypher file.
    Then, load all bioGrid genes and map them to genes:
        First, the gene Entrez ID is mapped to the gene identifier.
        Next, is the mapping of the gene symbol to gene unique gene symbol.
        The following mapping is between the gene symbol and the gene-gene symbols.
        The last mapping is gene symbol to gene synonyms.
    All mapping pairs are written into the TSV file.

The next program maps bioGRID chemical to chemical:
    First, it loads all chemicals and writes them into dictionaries.
    Next, it generates the mapping TSV file and adds a cypher query to the cypher file.
    Then, load all bioGrid chemicals and map them to chemicals. First, the identifier is prepared depending if it is a chemical node by reacting with a gene or a chemical that interacts with the gene-gene interaction.
        First, the InChIKey is mapped to the chemical InChIKey.
        Next, if the source is from DrugBank then this id is mapped to the chemical identifier.
        The last mapping is name to chemical name/synonyms.
    All mapping pairs are written into the TSV file.

The next program maps bioGRID disease to disease:
    First, it loaded all diseases and wrote them into dictionaries.
    Next, it generates the mapping TSV file and adds a cypher query to the cypher file.
    Then, load all bioGrid diseases and map them to diseases:
        First, the identifier (DOID) is mapped to the disease alternative IDs.
        The last mapping is name to disease name/synonyms.
    All mapping pairs are written into the TSV file.

The next program maps the bioGRID biological process (BP)/cellular component (CC) to BP/CC:
    For both BP and CC, the following steps were executed:
        First, it loads all nodes (BP/CC) and writes them into dictionaries.
        Next, it generates the mapping TSV file and adds a cypher query to the cypher file.
        Then, load all bioGrid BP/CC and map them to BP/CC:
            First, the identifier is mapped to the BP/CC identifier.
            Next, the identifier is mapped to the alternative identifier of BP/CC
        All mapping pairs are written into the TSV file.

All the mappings are integrated with the cypher file and the cypher-shell.

Next, protein-protein interaction (PPI) edges are prepared:
    First, load all PPI edge information into dictionaries and get the highest identifier number.
    For BP, CC, disease, and chemical the following step is executed:
        prepare a dictionary from interaction ID to label to set of identifiers of this label which are connected to the connection node.
    Then load all PPI (also the self-loops) and write the information into a dictionary and if multiple information for a pair exists add them to the list.
    Next, a cypher file is generated and the fitting cypher queries to add PPI edges and the connected disease, chemical, BP, and CC connection to the PPI edge are added as cypher queries.
    Additionally, TSV files for the different edges and the Interaction nodes are generated.
    Next, go through all PPI pairs of bioGRID and check if they exist already in PharMeBINet or not.
        If they exist the information is extracted from the existing pairs and the bioGrid information is merged and combined. Then they are written into the TSV file.
        If they do not exist the information is combined and prepared as a dictionary. Additionally, the identifier is added to the new PPI node. This information is written into the TSV file.

The last program prepares protein-chemical edges:
    First, load all kinds of chemical-protein edges and write them into dictionaries depending on the relationship types.
    Next, load all bioGRID chemical-protein pairs that are not from DrugBank and no other gene/protein interacts with. From them, only the one with a protein-action type target is considered. Only the edge type "inhibitor", "unknown", "modulator" and "activator" are considered and all information is written into a dictionary.
    Then, generate the different TSV files for mapping new edges and also prepare the different cypher queries and add them to the cypher file.
    Next, go through all bioGrid edges and check if the edge type and the pair already exist or not. The existing combines the information and is written into the TSV file and if not and multiple times the pair exists the information is also combined and written into the other TSV file.  

In the last step, the edge and edge nodes are integrated with the Neo4j cypher-shell and the cypher file.