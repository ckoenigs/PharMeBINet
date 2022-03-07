#!/bin/bash

../../../../neo4j-community-3.2.9/bin/neo4j-admin import --mode=csv --nodes output/neo4j_import/drugbank_compounds.csv --relationships output/neo4j_import/drug_target.csv --nodes output/neo4j_import/carrier_enzyme_target_transporter.csv --nodes output/neo4j_import/drugbank_metabolites.tsv --nodes output/neo4j_import/drugbank_pathway.tsv --nodes output/neo4j_import/drugbank_salt.tsv --nodes output/neo4j_import/drugbank_products.tsv --nodes output/neo4j_import/drugbank_mutated_gene_protein.tsv --nodes output/neo4j_import/drugbank_pharmacologic_class.tsv --nodes output/neo4j_import/drugbank_reactions.tsv --relationships output/neo4j_import/drugbank_target_mutated.tsv --relationships output/neo4j_import/drugbank_reaction_to_left_db.tsv --relationships output/neo4j_import/drugbank__reaction_to_left_dbmet.tsv --relationships output/neo4j_import/drugbank_reaction_to_right_db.tsv --relationships output/neo4j_import/drugbank_reaction_to_right_dbmet.tsv --relationships output/neo4j_import/drugbank_reaction_to_protein.tsv --relationships output/neo4j_import/drugbank_drug_pharmacologic_class.tsv --relationships output/neo4j_import/drugbank_drug_pathway.tsv --relationships output/neo4j_import/drugbank_drug_salt.tsv --relationships output/neo4j_import/drugbank_drug_products.tsv --relationships output/neo4j_import/drugbank_snp_effects.tsv --relationships output/neo4j_import/drugbank_snp_adverse_drug_reaction.tsv --relationships output/neo4j_import/drugbank_interaction.tsv --nodes output/neo4j_import/drugbank_enzyme.csv --relationships output/neo4j_import/drugbank_enzyme_pathway.csv --relationships output/neo4j_import/drugbank_target_peptide_has_component.tsv