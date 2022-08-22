The OMIM script mapped the OMIM gene and phenotypes to gene and disease and integrate the node information and edges.

The OMIM gene/phenotype is mapped to gene/disease.
               First, the gene mapping file is generated. Then, the fitting query to integrate is added to the cypher file.
               The OMIM genes are mapped to genes with the external reference from NCBI gene id (OMIM ids). The pairs are written into the TSV file.
               Next, the mapping and not mapping files for disease mapping are generated. Then, the query for the mapping between OMIM phenotype and disease is generated. Additionally, a cypher query for integrated not mapped phenotypes as phenotype into the database.
               The OMIM phenotypes are mapped to genes with external reference from NCBI gene identifiers (OMIM ids).
               The OMIM phenotypes are mapped to disease with the OMIM identifier to disease external reference OMIM identifier. Also, mapped with OMIM name to name and synonyms of PharMeBINet disease.
               All mapped pairs are written in the different TSV files. All not mapped phenotypes are written into the not mapped file.

The OMIM predominantly phenotypes are mapped to gene/disease.
               First, a mapping file for disease mapping is generated. For mapping to disease, the existing one is updated. Also, for the not mapped node, a TSV file is generated.
               Additionally, for the newly generated file, the fitting cypher queries are generated.
               The rest is like the OMIM phenotype steps.

Next, the mapping and creation information is integrated into the database with the cypher-shell.

The last program prepared the edge information from OMIM.
               First, all gene-disease/phenotype pairs are load into a dictionary.
               Then generate for each label pair a TSV file and the additional cypher query. In the following, the pair information is written into the TSV file.
               
The last step is the integration of the edges into the database with the cypher-shell.
