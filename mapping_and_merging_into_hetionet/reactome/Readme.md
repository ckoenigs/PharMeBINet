Reactome has also scripts because of the different mapping times!
First, some Reactome database modifications are made.  All species which are not human and connected to pathway are deleted. Next, all pathways which are not human are deleted. Then the figure URLs are added to the connected nodes and the figure node is deleted. The reference information (publication URL/LiteratureReference/Book) is integrated into the connected Reactome node and the reference nodes are deleted. All ReactionLikeEvent which are connected to the pathway and not human are deleted.

Next, a program to delete some reference information nodes which are harder to delete with a program (Summation and LiteratureRefernce).

Then two Reactome diseases have the same information as another node only another id. They are merged (2011833 1247632 and 9611565 3134792).

Next, all species which are not human are deleted with a program.

The next script mapped the Reactome pathway to pathway and add new pathways.
                First, the TSV files for mapping and new nodes are generated.
                Then it loads all pathway information into dictionaries.
                Next, load all Reactome pathways and map them with the Reactome identifier to pathway external reference Reactome identifier.
                The other mapping method is based on Reactome pathway name to pathway name.
                All mapped pairs are written into the mapped TSV file. The others are written into the new node TSV file.
                The last step generates the cypher file with the fitting cypher queries to integrate the mapping and the new nodes.
               
Next, the Reactome diseases are mapped to disease.
                First, the TSV files for mapping are generated.
                Then it loads all disease information into dictionaries.
                Next, load all Reactome diseases and map them with the DOID to disease DOIDs.
                The other mapping method is based on Reactome disease name to disease name.
                All mapped pairs are written into the mapped TSV file. The last step generates the fitting cypher queries to integrate the mapping pairs.


Then Reactome BP is mapped to BP.
                First, the TSV files for mapping are generated.
                Then it loads all BP information into dictionaries.
                Next, load all Reactome BP and map them with the GO identifier to BP GO identifier.
                The other mapping method is based on the Reactome BP GO identifier to BP alternative GO identifier.
                All mapped pairs are written into the mapped TSV file. The last step generates the fitting cypher queries to integrate the mapping pairs.

The same goes for Reactome CC to CC.
                This has the same steps as BP mapping only with CC.


The same goes for Reactome MF to MF.
                This has the same steps as BP mapping only with MF.

The cypher-shell integrates the mapped information and the new nodes.
Next, the cypher-shell integrates with another cypher file the nodes of ReactionLikeEvent (reaction, polymerization, depolymerization, black box event, failed reaction). But only human ReactionLike Event and such that have a pubmed ids.

The next program prepares the edges between FailedReaction and disease/pathway/ReactionLikeEvent/CC.
                First, generate the cypher file.
                For each FR-label-relationship type, the same steps are done.
                               First, generate the TSV file for the pair.
                               Next, load all pairs and check for no duplication. Then, add the pair to the TSV file.
                              The last step is to generate the cypher query to integrate the relationship into the database and add it to the cypher file.

The following program prepares the edges between pathway and disease/ ReactionLikeEvent/pathway/BP/CC.
                For each pathway-label-relationship type, the same steps are done.
                               First, generate the TSV file for the pair.
                               Next, load all pairs and check for no duplication. Then, add the pair to the TSV file.
                              The last step is to generate the cypher query to integrate the relationship into the database and add it to the cypher file.

The last program of the first script prepares the edge between reaction and ReactionLikeEvent/pathway/disease/BP.
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
               Then, the ReferenceEntities of Reactome is loaded and tried to map.
               The first mapping method is based on the IUPHAR identifier to chemical id (dictionary-IUPHAR to chemical id).
               Next, the other external reference to chemical external reference (ChEBI, KEGG Compound, PubChem Compound).
               Then, try to map with ReferenceEntity inn to chemical name.
               The last mapping method is based on mapping the ReferenceEntity names to chemical name. But check for strings with some HTML code inside and change to normal string.
               All mapped pairs are written into the TSV file.
               In the last step, the cypher file is generated, and add the cypher query to integrate the mapping.

Next, the PhysicalEntity is mapped to protein.
	First, generate a TSV file for the mapping file.
         Next, all protein information is loaded into dictionaries. 
               Then, the ReferenceEntities that are connected to PhysicalEntityy of Reactome are loaded and tried to map.
               The first mapping method is based on the UniProt identifier to protein UniProt identifier.
               Next, the other UniProt identifier to protein alternative UniProt identifier.
               All mapped pairs are written into the TSV file.
               In the last step, the cypher file is generated, and add the cypher query to integrate the mapping.
               
The cypher-shell integrates the mapping methods.

Next, the Reactome treat edges between drug, disease, and cc are prepared as meta-edge to integrate into the database.
               First, all pairs of drugs and disease and all drug-CC are loaded. The different information is added to the different dictionaries.
               Then, the TSV files for relationships between drug-treat-disease and treat-CC are generated. Additionally, the cypher file is generated. The cypher queries to integrate the node and relationships into the database are added to the cypher file.
               Next, all the disease-drug-treat information is written into the TSV file. The pairs which appear multiple times merge. Also, all treat-CC pairs are added to the other TSV file.
               
The following edge preparation is between PhysikalEntity (drug, protein) and ReactionLikeEvent.
	For each type of PhysikalEntity, the same steps are done.
		First, generate the TSV for the pairs.
		Next, load all pairs and write them into the TSV file.

Last, all other relationships between drugs and ReactionLikeEvents are prepared.
               For each pair label and relationship, the same step was executed.
                               First, the TSV file for the pair is generated.
                               Then, all pairs are loaded from Reactome and add to the TSV file.
                               In the last step, the cypher query of this pair is generated and add to the cypher file.

As the last step, the cypher-shell integrates the edges into the database.
