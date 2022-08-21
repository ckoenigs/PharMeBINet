# PharMeBINet: The heterogeneous pharmacological medical biochemical network
Heterogeneous biomedical pharmacological databases are important for multiple fields in bioinformatics.
The Hetionet database already covers many different entities. Therefore, it was used as the basis for this project. 20 different pharmacological medical and biological databases such as CTD, DrugBank, and ClinVar are parsed and integrated into Neo4j. Afterward, the information is merged into Hetionet. Different mapping methods were used such as external identification systems or name mapping.
The resulting open-source Neo4j database PharMeBINet has 2,869,407 different nodes with 66 labels and 15,883,653 relationships with 208 edge types. It is a heterogeneous database containing interconnected information on ADRs, diseases, drugs, genes, gene variations, proteins, and more. Relationships between these entities represent, for example, drug-drug interactions or drug-causes-ADR relations. It has much potential for developing further data analyses including machine learning applications. A web application for accessing the database is free to use for everyone and available at https://pharmebi.net. Additionally, the database is deposited on Zenodo at https://doi.org/10.5281/zenodo.5816976.

First, Hetionet (http://het.io) as a starting point was updated to Neo4j database service 4.2.5.
Afterward, the different data sources are parsed and integrated into Hetionet.
In the next step, the different data sources are mapped and merged into the Hetionet structure.
The final PharMeBINet database is then generated by removing the data source specific sub-graphs, leaving only the merged structure.

Included Data Sources:

| Data source     | Version    | License                                                                                                                                                                                  | URL                                                           |
|-----------------|:-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------|
| AEOLUS          | 2017-04-08 | [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)                                                                                                                  | [Link](http://datadryad.org/resource/doi:10.5061/dryad.8q0s4) |
| ClinVar         | 2022-05-05 | https://www.ncbi.nlm.nih.gov/home/about/policies/                                                                                                                                        | [Link](https://www.ncbi.nlm.nih.gov/clinvar/)                 |
| CTD             | 2022-04    | © 2002-2012 MDI Biological Laboratory. All rights reserved. © 2012-2021 NC State University. All rights reserved.                                                                        | [Link](http://ctdbase.org)                                    |
| dbSNP           | 2021-05-25 | https://www.ncbi.nlm.nih.gov/home/about/policies/                                                                                                                                        | [Link](https://www.ncbi.nlm.nih.gov/snp/)                     |
| DO              | 2022-04-28 | [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)                                                                                                                  | [Link](https://disease-ontology.org)                          |
| DrugBank        | 5.1.9      | [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)                                                                                                                          | [Link](https://go.drugbank.com)                               |
| Entrez Gene     | 2022-05-11 | https://www.ncbi.nlm.nih.gov/home/about/policies/                                                                                                                                        | [Link](https://www.ncbi.nlm.nih.gov/gene)                     |
| GO              | 2022-03-22 | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)                                                                                                                                | [Link](http://geneontology.org)                               |
| Hetionet        | 1.0        | [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)                                                                                                                  | [Link](https://het.io)                                        |
| HPO             | 2022-04-14 | This service/product uses the Human Phenotype Ontology (version information). Find out more at http://www.human-phenotype-ontology.org We request that the HPO logo be included as well. | [Link](https://hpo.jax.org)                                   |
| IID             | 2021-05    | Free to use for academic purposes                                                                                                                                                        | [Link](http://iid.ophid.utoronto.ca)                          |
| MONDO           | 2022-05-02 | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)                                                                                                                                | [Link](https://github.com/monarch-initiative/mondo)           |
| NDF-RT          | 2018-02-05 | UMLS license, available at https://uts.nlm.nih.gov/license.html                                                                                                                          | [Link](https://evs.nci.nih.gov/ftp1/NDF-RT/)                  |
| OMIM            | 2022-04-14 | https://www.omim.org/help/agreement                                                                                                                                                      | [Link](https://www.omim.org)                                  |
| Pathway Commons | 12         | License of the different sources                                                                                                                                                         | [Link](https://www.pathwaycommons.org)                        |
| PharmGKB        | 2022-05-05 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)                                                                                                                          | [Link](https://www.pharmgkb.org)                              |
| Reactome        | 2022-03-31 | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)                                                                                                                                | [Link](https://reactome.org)                                  |
| SIDER           | 4.1        | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)                                                                                                                    | [Link](http://sideeffects.embl.de)                            |
| UniProt         | 2022-01    | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)                                                                                                                                | [Link](https://www.uniprot.org)                               |
| WikiPathway     | 2022-04-10 | [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)                                                                                                                                | [Link](https://www.wikipathways.org)                          |

The shell script does the integration into neo4j and the mapping and merging to Hetionet.

```bash
./script_to_execute_all.sh /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-4.2.5/bin /home/cassandra/Documents/Project/master_database_change/ > output.txt 2>&1 &

./script_to_execute_all.sh /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-4.2.13/bin /home/cassandra/Documents/Project/master_database_change/ > output.txt 2>&1 &
```

## Citing this work
If you find this resource useful, please do remember to cite:

```bib
@article{konigs2022heterogeneous,
  title={The heterogeneous pharmacological medical biochemical network PharMeBINet},
  author={K{\"o}nigs, Cassandra and Friedrichs, Marcel and Dietrich, Theresa},
  journal={Scientific Data},
  volume={9},
  number={1},
  pages={1--14},
  year={2022},
  publisher={Nature Publishing Group}
}
```

ALternatively, using plain text, you can use:

Königs C, Friedrichs M, Dietrich T. [The heterogeneous pharmacological medical biochemical network PharMeBINet](https://www.nature.com/articles/s41597-022-01510-3). Scientific Data. 2022;9(1): 393.
