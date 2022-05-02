# PharmaMeBiNet: The heterogeneouspharmacological medicalbiochemical network
Fist use Hetionet (http://het.io/) as start base and was updated to Neo4j database service 4.2.5. First the different data source are parsed and then integrated into Neo4j database. In the next step the different database are mapped and merged intho Hetionet and generate the database PharmaMeBiNet

Heterogeneous biomedical pharmacological databases are important for multiple fields in bioinformatics.
The Hetionet database already covers many different entities. Therefore, it was used as the basis for this project. 19 different pharmacological medical and biological databases such as CTD, DrugBank, and ClinVar are parsed and integrated into Neo4j. Afterward, the information is merged into Hetionet. Different mapping methods were used such as external identification systems or name mapping.
The resulting open-source Neo4j database PharMeBINet has 2,385,126 different nodes with 66 labels and 15,158,839 relationships with 233 edge types. It is a heterogeneous database containing interconnected information on ADRs, diseases, drugs, genes, gene variations, proteins, and more. Relationships between these entities represent, for example, drug-drug interactions or drug-causes-ADR relations. It has much potential for developing further data analyses including machine learning applications. A web application for accessing the database is free to use for everyone and available at https://pharmebi.net and https://doi.org/10.5281/zenodo.5816976

Included Data:

| Data source   |      Version      |  License | URL |
|----------|:-------------:|------|---------------|
| AEOLUS |  2017-04-08 | CC0 1.0 Universal (CC0 1.0) Public Domain Dedication license  | [Link](http://datadryad.org/resource/doi:10.5061/dryad.8q0s4) |
| ClinVar |    2022-04-07   |   https://www.ncbi.nlm.nih.gov/home/about/policies/ | [Link](https://www.ncbi.nlm.nih.gov/clinvar/) |
| CTD | 2022-04 | © 2002-2012 MDI Biological Laboratory. All rights reserved. © 2012-2021 NC State University. All rights reserved. | [Link](http://ctdbase.org/) |
| dbSNP |    2021-05-25  |   https://www.ncbi.nlm.nih.gov/home/about/policies/policies/ | [Link](https://www.ncbi.nlm.nih.gov/snp/) |
| DO |    2022-04-28   |   CC0 1.0 Universal | [Link](https://disease-ontology.org/) |
| DrugBank |    5.1.9   |   Creative Common's Attribution-NonCommercial 4.0 International License | [Link](https://go.drugbank.com/) |
| Entrez Gene |    2022-04-28   |   https://www.ncbi.nlm.nih.gov/home/about/policies/ | [Link](https://www.ncbi.nlm.nih.gov/gene) |
| GO |    2022-03-22   |   CC0 4.0 International | [Link](http://geneontology.org/) |
| Hetionet |    V1.0  |   CC0 1.0 Universal (CC0 1.0) Public Domain Dedication  | [Link](https://het.io/) |
| HPO |    2022-04-14   |   This service/product uses the Human Phenotype Ontology (version information). Find out more at http://www.human-phenotype-ontology.org We request that the HPO logo be included as well. | [Link](https://hpo.jax.org) |
| IID |    2021-05   |   Free to use for academic purposes | [Link](http://iid.ophid.utoronto.ca/) |
| MONDO |    2022-04-04   |   CC BY 4.0 | [Link](https://github.com/monarch-initiative/mondo) |
| NDF-RT |    2018-02-05   |   UMLS license, available at https://uts.nlm.nih.gov/license.html | [Link](https://evs.nci.nih.gov/ftp1/NDF-RT/) |
| OMIM |    2022-04-14   |   https://www.omim.org/help/agreement | [Link](https://www.omim.org/) |
| Pathway Commons |    V 12   |   License of the different sources | [Link](https://www.pathwaycommons.org/) |
| PharmGKB |    2022-04-05   |   Creative Commons Attribution-ShareALike 4.0 license | [Link](https://www.pharmgkb.org/) |
| Reactome |    2022-03-31   |   Creative Commons Attribution 4.0 International (CC BY 4.0) License | [Link](https://reactome.org/) |
| SIDER |    V 4.1   |   Creative Commons Attribution-Noncommercial-Share Alike 4.0 License | [Link](http://sideeffects.embl.de/) |
| UniProt |    2022-01   |   CC BY 4.0 | [Link](https://www.uniprot.org/) |
| WikiPathway |    2022-04-10   |   CC BY 3.0 | [Link](https://www.wikipathways.org/index.php/WikiPathways) |

The shell script do the integration into neo4j and the mapping and merging to Hetionet.

./script_to_execute_all.sh /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-4.2.5/bin /home/cassandra/Documents/Project/ > output.txt 2>&1 &

./script_to_execute_all.sh /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-4.2.13/bin /home/cassandra/Documents/Project/ > output.txt 2>&1 &


