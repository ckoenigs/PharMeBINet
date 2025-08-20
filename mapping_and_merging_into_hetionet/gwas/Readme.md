The GWAS Catalog script contains multiple steps.
First, map the GWAS catalog trait to phenotype and biological process (BP):
    First, load all diseases, symptoms, phenotypes, and BP into dictionaries.
    Next, generate two TSV files for mapping to phenotype and for mapping to BP. Additionally, a cypher file with two cypher queries is generated.
    Last, all traits are loaded and mapped; therefore, first, the trait ID is prepared for the different mappings:
        First, map the trait ID to BP and phenotype.
        Next, if the trait ID is efo, then it is mapped to the disease xref efo ID.
        Next, with efo id to symptom xref efo id.
        Then mapped to the symptoms HPO ID.
        Next, mapped with trait name to disease name.
        Then, to the symptoms' name.
        In the following, it is mapped to the phenotype name.
        Next, a manual mapping is used.
        Then, the trait ID is mapped to the disease xref orphanet ID.
        Then, the name is mapped to the disease synonyms.
        In the following, the trait name is mapped to UMLS CUI through UMLS to the disease xrefs UMLS CUI.
        Then, the name is mapped to the symptom synonyms.
        In the following, the trait name is mapped to UMLS CUI through UMLS to the symptom xrefs UMLS CUI.
        Then, the trait name is mapped to UMLS CUI through UMLS to the phenotype xrefs UMLS CUI.
        Then, the name is mapped to the phenotype synonyms.
        Last, with the mapped UMLS CUIs from UMLS, additional mapping to NCIT with UMLS to disease xrefs NCIT ID.
    All pairs are written into the TSV files.


Next, the GWAS Catalog associations are mapped to Variant:
    First, load all rs variants nodes into dictionaries.
    Next, generate TSV files for mapping and not mapping, and add two Cypher queries to the Cypher file. One query for mapping and one for adding new nodes.
    Then, load all associations that are not a combined SNPs and map them to a variant. Therefore, the identifier is parsed if it has an rs id:
        The association rs ID is mapped to the variant identifier.
        The not-mapped rs IDS are written in the not-mapped TSV file.

Then, with the Neo4j Cypher shell, the mappings and new nodes are added to PharMeBINet.

Next, the variant-disease/symptom/side effect/ phenotype edges are added:
    First, generate a cypher file.
    Then, load all GWAS catalog studies that have publications as references.
    Next, load existing variant-SE/symptom/phenotype edges and write information into dictionaries.
    Load all variant-phenotyp edges from GWAS from association to study to trait.
        Extract the most specific label of the phenotype and prepare edge information.
        Then, go through all pairs and combine multiple information and mappings to existing edges.
        Additionally, create for each edge type a mapping and a new TSV file, adding Cypher queries to the Cypher file.
        In the different TSV files, the pairs are added.
    Last, a similar to variant-phenotype is executed for variant-BP. The only exception is that no label check is needed.



