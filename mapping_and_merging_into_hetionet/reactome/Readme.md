There exist multiple mapping scripts

The first script starts with mapping the Reactome pathway to pathways and adding new pathways.
                First, the TSV files for mapping and new nodes are generated.
                Then it loads all pathway information into dictionaries.
                Next, load all Reactome pathways and map them with the Reactome identifier to pathway external reference Reactome identifier.
                The other mapping method is based on the Reactome pathway name to pathway name.
                All mapped pairs are written into the mapped TSV file. The others are written into the new node TSV file.
                The last step generates the cypher file with the fitting cypher queries to integrate the mapping and the new nodes.
               
Next, the Reactome diseases are mapped to the disease.
                First, the TSV files for mapping are generated.
                Then it loads all disease information into dictionaries.
                  Next, load all Reactome diseases and map them with the DOID to disease DOIDs.
                  The other mapping method is based on Reactome disease name to disease name.
                  The last, mapping method is based on Reactome name to disease synonyms.
                All mapped pairs are written into the mapped TSV file. The last step generates the fitting cypher queries to integrate the mapping pairs.


Then Reactome BP is mapped to BP.
                First, the TSV files for mapping are generated.
                Then it loads all BP information into dictionaries.
                Next, load all Reactome BP and map them with the GO identifier to the BP GO identifier.
                The other mapping method is based on the Reactome BP GO identifier to the BP alternative GO identifier.
                All mapped pairs are written into the mapped TSV file. The last step generates the fitting cypher queries to integrate the mapping pairs.

The same goes for Reactome CC to CC.
                This has the same steps as BP mapping only with CC.


The same goes for Reactome MF to MF.
                This has the same steps as BP mapping only with MF.

The cypher-shell integrates the mapped information and the new nodes.
Next, the cypher-shell integrates with another cypher file the nodes of ReactionLikeEvent (reaction, polymerization, depolymerization, black box event, failed reaction). But only human ReactionLikeEvent and such have PubMed ids.

The next program prepares the edges between ReactionLikeEvent and disease/pathway/ReactionLikeEvent/CC/BP.
                First, generate the cypher file.
                For each RLE-label-relationship type, the same steps are done.
                               First, generate the TSV file for the pair.
                               Next, load all pairs and check for no duplication. Then, add the pair to the TSV file.
                              The last step is to generate the cypher query to integrate the relationship into the database and add it to the cypher file.

The following program prepares the edges between pathway and disease/ ReactionLikeEvent/pathway/BP/CC.
                For each pathway-label-relationship type, the same steps are done.
                               First, generate the TSV file for the pair.
                               Next, load all pairs and check for no duplication. Then, add the pair to the TSV file.
                              The last step is to generate the cypher query to integrate the relationship into the database and add it to the cypher file.

The last program of the first script prepares the edge between reaction and RLE/pathway/disease/BP/CC.
                For each reaction-label-relationship type, the same steps are done.
                               First, generate the TSV file for the pair.
                               Next, load all pairs and check for no duplication. Then, add the pair to the TSV file.
                              The last step is to generate the cypher query to integrate the relationship into the database and add it to the cypher file.

Lastly, the cypher-shell integrates the edges into the database.
 
The next script is later because the compounds and chemicals must be added before.

First, the Reactome drug and physical entity are tried to be mapped chemical.
               First, generate a TSV file for the mapping file.
               Then, IUPHAR data is loaded into dictionaries.
               Next, all chemical information is loaded into dictionaries. Also, prepare a dictionary from IUPHAR identifier to chemical identifier with the use of InChI.
               Then, the ReferenceEntities of Reactome are loaded and tried to map.
               The first mapping method is based on the IUPHAR identifier to chemical id (dictionary-IUPHAR to chemical id).
               Next, the other external reference to chemical external reference (ChEBI, KEGG Compound, PubChem Compound).
               Then, try to map with ReferenceEntity inn to chemical names.
               The last mapping method is based on mapping the ReferenceEntity names to chemical names. But check for strings with some HTML code inside and change them to a normal strings.
               All mapped pairs are written into the TSV file.
               In the last step, the cypher file is generated, and add the cypher query to integrate the mapping.

Next, the PhysicalEntity is mapped to the protein.
      First, generate a TSV file for the mapping file.
         Next, all protein information is loaded into dictionaries. 
               Then, the ReferenceEntities that are connected to the PhysicalEntity of Reactome are loaded and tried to map.
               The first mapping method is based on the UniProt identifier to protein UniProt identifier.
               Next, the other UniProt identifier to protein alternative UniProt identifier.
               All mapped pairs are written into the TSV file.
               In the last step, the cypher file is generated, and add the cypher query to integrate the mapping.
               
The cypher-shell integrates the mapping methods.

Next, the Reactome treatment edges between drug, disease, and cc are prepared as meta-edge to integrate into the database.
               First, all pairs of drugs and diseases and all drug-CC are loaded. The different information is added to the different dictionaries.
               Then, the TSV files for relationships between drug-treat-disease and treat-CC are generated. Additionally, the cypher file is generated. The cypher queries to integrate the node and relationships into the database are added to the cypher file.
               Next, all the disease-drug-treat information is written into the TSV file. The pairs which appear multiple times merge. Also, all treat-CC pairs are added to the other TSV file.
               
The following edge preparation is between PhysikalEntity (drug, protein) and ReactionLikeEvent.
      For each type of PhysikalEntity, the same steps are done.
            First, generate the TSV for the pairs.
            Next, load all pairs and write them into the TSV file.
            Create the cypher query to integrate the edge from the TSV file.

The following edge preparation is between Regulation, and chemical, protein, and GO.
      For each type of edge type and label (chemical, protein, and GO), the same steps are done.
            First, generate the TSV for the pairs.
            Next, load all pairs and write them into the TSV file.
            Create the cypher query to integrate the edge from the TSV file.

The following interaction edge preparation is between chemical, and chemical, and protein.
      First, the existing compound-compound interactions are loaded in.
      Then, for each type of edge type and label (chemical, protein), the same steps are done.
            First, generate the TSV for the pairs.
            Next, load all pairs and check if they are new or existing interactions.
            Then write the new and the existing interactions in the different tsv files.
            Create the cypher query to integrate the edge from the TSV file.

The following interaction edge preparation is between protein and protein. This is solo because the PPIs have an interaction node and not only an edge.
      First, the existing protein-protein interactions are loaded in.
      First, generate the TSV for the pairs.
      Next, load all pairs and check if they are new or existing interactions.
      Then write the new and the existing interactions in the different tsv files.
      Create the cypher query to integrate the edge from the TSV file.


The following edge preparation is between MolecularComplex, and chemical, protein, ReactionLikeEvent, MolecularComplex, Regulation, and GO.
      For each type of edge type and label (chemical, protein, MolecularComplex, ReactionLikeEvent, Regulation, and GO), the same steps are done.
            First, generate the TSV for the pairs.
            Next, load all pairs and write them into the TSV file.
            Create the cypher query to integrate the edge from the TSV file.


The next programs separate the CatalysticActivity (CA) node into separate edges.
The first prepare activity edges between RLE and MolecularComplex, and protein.
      Therefore, first load all CA nodes with the fitting CAReference node and save them in a dictionary.
      For each label ( protein, MolecularComplex), the same steps are done.
            First, generate the TSV for the pairs.
            Next, load all pairs where the CA is in the dictionary with the reference information and write them into a dictionary that combines CA information from the same pairs.
            Next, the combined information is written into the TSV file.
            Create the cypher query to integrate the edge from the TSV file.

Next, prepare molecular function edges between MF and MolecularComplex, and protein.
      Therefore, first load all CA nodes with the fitting CAReference node and save them in a dictionary.
      For each label ( protein, MolecularComplex), the same steps are done.
            First, generate the TSV for the pairs.
            Next, load all pairs where the CA is in the dictionary with the reference information and write them into a dictionary that combines CA information from the same pairs.
            Next, the combined information is written into the TSV file.
            Create the cypher query to integrate the edge from the TSV file.

The last get component connections from the CA nodes. So, this generates connections between MolecularComplex and MolecularComplex, and protein:
      For each label ( protein, MolecularComplex), the same steps are done.
            First, generate the TSV for the pairs.
            Next, load all pairs and write them into the TSV file.
            Create the cypher query to integrate the edge from the TSV file.


As the last step, the cypher-shell integrates the edges into the database.
