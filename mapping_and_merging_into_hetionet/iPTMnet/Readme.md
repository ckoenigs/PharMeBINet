Next, map the iPTMnet proteins to proteins:
	 First, load all PharMeBINet protein information into dictionaries, and also the gene-protein connection information.
	 Next, prepare the mapping TSV file, open the existing cypher file, and write the mapping query.
	 Last, load all proteins from the human and map them:
	 First, mapping with UniProt identifier.
	 Next, map the split isoform  UniProt identifier to the protein identifier.
			Then, map the gene name to gene to the protein in PharMeBINet.
	 In the following, it is mapped with an alternative UniProt ID.
	 Last, map the name to the protein name.
	 All mapping pairs are written into the TSV file.
	
Then the mappings are integrated into PharMeBINet with the Neo4j cypher shell.

Next, the iPTMnet PTMs are mapped and added to PharMeBINet:
	 First, load all PTMs into a dictionary.
		Then, generate TSV files for new and mapped PTMs, and generate a cypher file with the additional cypher queries.
	 Last, load all PTMD PTMs that are connected to mapped PTMD proteins:
	 First, the identifier is generated based on the UniProt ID, position, residue, and ptm type.
	 All PTM that contains all information for the identifier are written into the TSV file.
 
Then the mappings and add of PTMs are integrated into PharMeBINet with Neo4j cypher shell.

Last, the PTMD PTM-protein edges are added (All the involved edges only have on the Website pubmed ids.):
	 First, prepare the cypher file.
		Then, load all PTM-Protein edges from PharMeBINet and write them into dictionaries for the different edge types.
		For both edge types, do the following:
	 Next, prepare the new and mapped edge files as TSV and write the queries into the cypher file.
	 Then, load all iPTMnet PTM-protein edges in batches, filter to only those with PubMed or from specific sources (for the involves all are excepted), and write into the different TSV files.

 
Last, add and merge the iPTMnet edges into PharMeBINet with the Neo4j cypher shell.

https://research.bioinformatics.udel.edu/iptmnet/

## Selected Databases from iPTMnet
### Overview

This document outlines the selected databases utilized from iPTMnet for post-translational modification (PTM) data analysis. These databases were chosen based on their reliability, relevance, and the quality of curated information.

---

### Selected Databases

#### 1. **PhosphoSitePlus (psp)**
#### 2. **UniProt (unip)**
#### 3. **PRO (pro)**
#### 4. **RLIMS-P+ (rlim+)**
#### 5. **Signor (sign)**
#### 6. **PomBase (pomb)**
#### 7. **neXtProt (npro)**

---

The edges between protein and PTM has and involve getting a property as a flag if only the isoforms have this connection.
