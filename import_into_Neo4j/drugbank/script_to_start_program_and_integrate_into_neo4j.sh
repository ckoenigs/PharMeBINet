#!/bin/bash
now=$(date +"%F %T")
echo "Current time: $now"
echo information extraction from xml

#python transform_drugbank_to_tsv.py > output_transform.txt



now=$(date +"%F %T")
echo "Current time: $now"
echo file preperation

output_file=output_file_preperation.txt

python file_preperation.py "/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/Drugbank_database/drugbank_files_without_preperation/" drug_sequences/ external_links/ Protein_identifiers/ structure/ target_sequences/ > $output_file

#exit 1

cd output
echo test
now=$(date +"%F %T")
echo "Current time: $now"
echo combine

cat drugbank_Enzyme_DrugBank_2.tsv >> drugbank_Enzyme_DrugBank.tsv

#exit 1

now=$(date +"%F %T")
echo "Current time: $now"
echo integration with cypher shell

cat cypher_file.cypher | ../../../../../neo4j-community-3.2.9/bin/cypher-shell -u neo4j -p test > cypher_output.txt

cat cypher_rela_file.cypher | ../../../../../neo4j-community-3.2.9/bin/cypher-shell -u neo4j -p test

