PharmGKB has two scripts because by the edges the variants must be validated.

The first script map the different pharmGKB nodes to the database nodes.
The first program maps pharmGKB gene to gene.
    First, load the database genes into a dictionary with gene id/gene symbol/synonyms as key.
    Next, the mapping TSV file and the cypher file are generated. Additionally, a cypher query is generated and add to the cypher file to integrate the mapping information into the database. 
    The pGKB genes are mapped to the gene with the NCBI identifier of pGKB to the identifier. The next, mapping method uses the pGKB symbol to the gene gene-symbol. The last mapping method is the mapping between pGKB symbol to gene synonyms.
    All pairs are written into the TSV file.

Next, the pharmGKB chemical is mapped to chemical/PC.
    First, load the chemical and PC information into dictionaries.
    Next, the different mapping TSV files are generated. Additionally, the fitting cypher queries are generated and added to the cypher file.
    The first mapping method to chemicals is based on the InChI.
    Next, the external reference of pGKB DrugBank id is mapped to DrugBank id of chemical.
    Next, the external reference of ndf-rt id to NDF-RT identifier of pc if it is type drug class.
    Then it is mapped from the PubChem id to the chemical external reference PubChem id.
    The following mapping method is based on the pGKB MESH id to the chemical MESH id.
    The next mapping method is name to name/synonym.
    All nodes which did not map before and have type drug class are tried to mapped to PC with name.
    Then it is tried to mapped pGKB chemical with generic names to name/synonyms.
    In the last mapping try the chemical name is mapped to UMLS UMLS Cui and from there with UMLS to MESH or DrugBank id.
    All pairs are written into the different TSV files.

Then the pharmGKB haplotype and variant are mapped to variant.
    First, all variant information is loaded into dictionaries.
    The for pGKB variant and haplotype the same is done.  First, generate the mapping TSV files for mapping and new nodes.
    Then generate the fitting cypher queries and add them to the cypher file.
    The first mapping method is the pGKB variant/haplotype name to variant external reference dbSNP id.
    Next, the mapping of pGKB variant/haplotype name to variant name.
    All mapped pairs are written into the TSV files. Only the not mapped nodes with a dbSNP id are add to the new TSV files.

The last mapping is mapping pharmGKB to disease/symptom/SE and generate new phenotype nodes.
    First, all mapping information for disease/symptom/SE is load in dictionaries.
    Then the TSV files for the different mapping labels and the new node are generated. Additionally, the fitting cypher queries are generated and add to the cypher file.
    The first mapping method is from phenotype name to disease name/synonyms.
    Then phenotype external reference SnoMed id to disease external reference SnoMed id.
    The last mapping to disease is with the external reference UMLS Cui to UMLS Cui.
    The first mapping to symptom use phenotype name to symptom name/synonyms.
    The next is phenotype UMLS Cui to external reference UMLS Cui from symptom.
    The first mapping to SE is also with a name to name/synonym.
    Also, the phenotype UMLS Cui is mapped to SE UMLS Cui.
    All mapped pairs are written into the different TSV files. The not mapped are written into the new TSV file.

The cypher-shell integrates the mapping information and the new nodes into the database.         

The next script starts with the preparation of variant-gene connection from pGKB.
    First, the TSV file is generated. Then the query to merge the gene variant information is added to the generated cypher file.
    All variant-gene pairs are extracted from pGKB which are mapped to the database. The information is written into the TSV file.

Next, the preparation of the clinicalAnnotation is generated.
    Therefore, the TSV file is generated for the clinicalAnnotation (CA). The CA allele information are added to the CA nodes, but only CA which has at least level of evidence>=3. Additionally, a cypher query to integrate these meta-edges into the database is added to the cypher file. Next for all pairs CA-variant/chemical/pc/gene/phenotype the TSV files are generated and additional cypher queries are added.
    Next, get all CAM where the pGKB chemical is connected to chemical or pc and pGKB variant/haplotype are connected to the variant with ClinicalAnnotation.
    The CA are prepared for the CAM as properties genotypes and clinical phenotype.
    In the following step, the CAM information is written into the TSV file.
    The last step is to write the different relationship pairs in the different TSV files.

The last program prepares the integration of the different VariantAnnotation into the database.
    For all VA (except of the non significance) first the TSV file for the meta-edge is generated with the additional cypher query.  Then all studyParameter are loaded and generate a VA-sp dictionary.
    Then all VA from this type with a mapped variant/haplotype is loaded. The SPs are prepared as JSON property of the VA. All information is written into the TSV file.
    Then a query is added to integrate a relationship between CAM and VA.
    Then all pairs of VA-chemical/gene/pc/variant are loaded and written into the different TSV files.
    The last step is to generate delete queries where one of the nodes which are connected to VA is not mapped. These are also mapped to the cypher file.

The last step is to integrate the new meta-edge and the different relationships with the cypher-shell into the database.