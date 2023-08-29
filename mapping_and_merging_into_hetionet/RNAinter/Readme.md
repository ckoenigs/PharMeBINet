The script start with mapping RNAinter DNA to gene:
    First, load the RNAinter DNA and write information into dictionary.
    Next, generate TSV file.
    Then, load all gene nodes and map them to RNAinter NCBI id. The mappings are written into the TSV file.
    In the last step, the cypher file is generated and the fitting cypher query is added.

Next, is the mapping between RNAinter protein and protein:
    First, load the RNAinter proteins and write information into a dictionary.
    Then, load the protein information and map with uniprot identifier to RNAinterprotein uniprot id.
    The next mapping is with NCBI gene id to gene which is connected to a protein.
    All mapping pairs are written into a dictionary.
    Then, a TSV file is generated and the mapping pairs are written into it.
    In the last step a cypher query is generated and add to the cypher file.

The following, maps RNAinter compounds to chemicals:
    First, load all chemical information into dictionaries.
    Secondary, Generate the TSV file.
    Then, load the RNAinter compounds an map them to chemicals:
        First, mapping is with raw id to the chemical identifier.
        Secondary, mapping with raw id to chemical xref pubchem id.
        Next, is mapping with raw id to name/synonym of chemical.
        The last mapping is with name to name/synonym of chemical.
    All mapping pairs are written into the TSV file.
    In the last step, the cypher query is generated and add to the cypher file.


Then, map RNAinter RNAs to RNAs:
    First, load all RNA information into dictionaries.
    Then, load all gene-RNA infrmation into dictionary.
    Next, Generate the TSV file.
    Then, load the RNAinter RNAs an map them to RNAs:
        First, mapping is with raw id Ensembl to the RNA xrefs Ensembl id.
        Secondary, mapping with raw id miRBase to chemical xref miRBase id (onla if it is a miRNA and not starts with MIMAT).
        Next, is mapping with raw id NCBI to gene identifier wthat is connected to RNA.
        Then, map the RNAinter Interactor (only if source is miRBase) to RNA product.
        The RNAinter raw id is mapped to the RNA gene property.
        Next, the RNAinter INteractor is mapped to the RNA gene property.
        The last mapping is with raw id to name of RNA.
    All mapping pairs are written into the TSV file.
    In the last step, the cypher query is generated and add to the cypher file.

The cypher queries are executed with Neo4j cypher-shell.

The last programm, prepare the differene edge information RNA-RNA/gene/chemical/protein:
    First, generate a cypher file.
    Then, for gene/protein/RNA/chemical the following steps are executed:
        First, a TSV file is generated.
        Then, the edges are loaded in batches because the collect takes a lot of memory. Also only edges with a score over 0.5 are used. The edge information for a pair are combined.
        All pairs are written into the TSV file.
        Last, the cypher query is prepared and add to the cypher query.

Last, the cypher queries are executed with Neo4j cypher-shell.


