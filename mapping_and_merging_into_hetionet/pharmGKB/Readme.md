PharmGKB has two scripts because by the edges the variants must be validated.

The first script maps the different pharmGKB nodes to the database nodes.
The first program maps pharmGKB gene to gene.
    First, load the database genes into a dictionary with gene ID/gene symbol/synonyms as key.
    Next, the mapping TSV file and the cypher file are generated. Additionally, a cypher query is generated and added to the cypher file to integrate the mapping information into the database. 
        The pGKB genes are mapped to the gene with the NCBI identifier of pGKB to the identifier. 
        Then, the pGKB gene HGNC IDs are mapped to the gene HGNC IDs.
        The next, mapping method uses the pGKB symbol to the gene gene-symbol. 
        The last mapping method is the mapping between the pGKB symbol to gene synonyms.
    All pairs are written into the TSV file.

Next, the pharmGKB chemical is mapped to chemical/PC.
    First, load the chemical and PC information into dictionaries.
    Next, the different mapping TSV files are generated. Additionally, the fitting cypher queries are generated and added to the cypher file.
    Then, the pGKB chemicals are loaded and mapped:
        The first mapping method for chemicals is based on the InChI.
        Next, the external reference of the pGKB DrugBank ID is mapped to the DrugBank ID of the chemical.
        Next, the external reference of NDF-RT id to NDF-RT identifier of pc if it is type drug class.
        Then, it is mapped from the PubChem ID to the chemical external reference PubChem ID.
        The following mapping method is based on the pGKB MESH id to the chemical MESH id.
        The next mapping method is name-to-name/synonym.
        All nodes that did not map before and have type drug class are tried to mapped to PC with name.
        Then it is tried to map pGKB chemical with generic names to name/synonyms.
        In the last mapping try the chemical name is mapped to UMLS UMLS Cui and from there with UMLS to MESH or DrugBank id.
    All pairs are written into the different TSV files.

Then the pharmGKB haplotype and variant are mapped to the variant.
    First, all variant information is loaded into dictionaries.
    The for pGKB variant and haplotype the same is done.  
        First, generate the mapping TSV files for mapping and new nodes.
        Then, generate the fitting cypher queries and add them to the cypher file.
        Next, load all pGKB nodes (variant/haplotype) and map them:
            The first mapping method is the pGKB variant/haplotype name to variant identifier dbSNP id.
            Next, the mapping of pGKB variant/haplotype name to variant name.
        All mapped pairs are written into the TSV files. Only the not-mapped nodes with a dbSNP ID are added to the new TSV files.

The last mapping is mapping pharmGKB to disease/symptom/SE and generating new phenotype nodes.
    First, all mapping information for disease/symptom/SE is loaded in dictionaries.
    Then, the TSV files for the different mapping labels and the new node are generated. Additionally, the fitting cypher queries are generated and added to the cypher file.
    Next, all pGKB phenotypes are loaded and mapped:
        The first mapping method is from phenotype name to disease name/synonym.
        Then phenotype external reference SnoMed id to disease external reference SnoMed id.
        The last mapping to disease is with the external reference UMLS Cui to UMLS Cui.
        The first mapping to symptom uses phenotype name to symptom name/synonyms.
        The next is phenotype UMLS Cui to external reference UMLS Cui from symptom.
        The first mapping to SE is also with a name-to-name/synonym.
        Also, the phenotype UMLS Cui is mapped to SE UMLS Cui.
    All mapped pairs are written into the different TSV files. The not mapped are written into the new TSV file.

The cypher-shell integrates the mapping information and the new nodes into the database.         

The next script starts with the preparation of variant-gene connection from pGKB:
    First, the TSV files are generated. Then the queries to merge the gene variant information are added to the generated cypher file.
    All variant-gene pairs are extracted from pGKB which are mapped to the database. The information is written into the TSV files.

Next, the preparation of the clinical annotation (CA) is generated.
    First, go through all CA edge which has a connection to the variant/gene/phenotype of pGKB but go not to the variant/gene/phenotype of PharMeBINet and save the IDs in a set.
    The same is done for PC edge to chemical but not connect to chemical or PC of PharMeBINet.
    Next, all CA-CAAllel information is loaded and written into a dictionary.
    Therefore, the TSV file is generated for the CA. The CA allele information is added to the CA nodes, but only CA which has at least a level of evidence>=3 and is not in the set of have not a connection to PharMeBINet. Additionally, a cypher query to integrate these meta-edges into the database is added to the cypher file. Next for all pairs CA-variant/chemical/pc/gene/phenotype the TSV files are generated and additional cypher queries are added.
    Next, the different edge pairs are loaded and written into the different TSV files but only the CA which are added as nodes.

The last program prepares the integration of the different VariantAnnotation (VA) into the database.
    First, go through all VA edge which has a connection to the variant/gene/phenotype of pGKB but go not to the variant/gene/phenotype of PharMeBINet and save the IDs in a set.
    The same is done for PC edge to chemical but not connect to chemical or PC of PharMeBINet.
    Next, load VA-Studyparameters and save the information in a dictionary.
    The VA-Literature edges are loaded and from these PubMed IDs, PubMed central IDs, and guidelines URLs are extracted and written into a dictionary.
    Next, for each of the VA (PharmGKB_VariantDrugAnnotation, PharmGKB_VariantFunctionalAnalysisAnnotation, PharmGKB_VariantPhenotypeAnnotation) the following steps are executed:
        First, the TSV file for the meta-edge is generated with the additional cypher query. 
        Next, load all VAs of this type that are significant. Then, remove all VAs that are in the set of not all connected to PharMeBINet. All nodes get if they have the literature and study parameters.
        The information is written into the TSV file.
    Next, prepare the different TSV files, and the additional cypher queries are added.
    Then a query is added to integrate a relationship between CA and VA.
    Then all pairs of VA-chemical/gene/pc/variant are loaded and written into the different TSV files.
    The last step is to generate delete queries where one of the nodes that are connected to VA is not mapped. These are also added to the cypher file.

The last step is to integrate the new meta-edge and the different relationships with the cypher-shell into the database.
