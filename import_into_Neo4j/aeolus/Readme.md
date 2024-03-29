This integrates only the drug and outcome data from AEOLUS into Neo4j.

The AEOLUS data (April 8, 2017) can be download by http://datadryad.org/resource/doi:10.5061/dryad.8q0s4. 

The data of AEOLUS are all tsv files.

standard_case_drug.tsv: Aggregated and mapped information found in the DRUGyyQq files from LAERS and FAERS.
Generate a dictionary from case id (primaryid, isr) to drug_seq to drug_concept ids

indications.tsv: Mapped indication preferred terms from the INDIyyQq files into OHDSI standard vocabulary concept identifiers and SNOMEDCT concept identifiers.
Generate with the dictionary before a set of drug-indication tuples. Write the tuple in to indication file.

concept.tsv: OHDSI vocabulary version v5.0 08-JUN-15 concepts.
Prepare a dictionary from concept id to concept information.

standard_drug_outcome_statistics.tsv: Features for all drug-outcome pairs the PPR and ROR with their 95% confidence interval (upper and lower values).
Prepare a dictionary from drug-outcome pair to edge information about statistics!

standard_drug_outcome_contingency_table.tsv: Contains all calculated 2x2 contingency tables for all drug-outcome combinations found in the data.
Add to the edge information the contingency table entries.

In the last step, the cypher queries are generated to integrate the outcome/indications, drugs, and the relationships between drug and outcome/indication as to cause or indicates. 
Additionally, the TSV files for outcome/indication, drug, and relationships are generated.


License: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

Banda JM, Evans L, Vanguri RS, Tatonetti NP, Ryan PB, Shah NH (2016) A curated and standardized adverse drug event resource to accelerate drug safety research. Scientific Data 3: 160026. https://doi.org/10.1038/sdata.2016.26

Banda JM, Evans L, Vanguri RS, Tatonetti NP, Ryan PB, Shah NH (2016) Data from: A curated and standardized adverse drug event resource to accelerate drug safety research. Dryad Digital Repository. https://doi.org/10.5061/dryad.8q0s4