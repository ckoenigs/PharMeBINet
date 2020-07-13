#!/bin/bash

#projekt path
path_to_project=$1

# path to neo4j
path_neo4j=$2


echo  $path_neo4j

now=$(date +"%F %T")
echo "Current time: $now"
echo information extraction from xml

python3 transform_drugbank_to_tsv.py > output_transform.txt



now=$(date +"%F %T")
echo "Current time: $now"
echo file preperation

output_file=output_file_preperation.txt

python3 file_preperation.py "/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/Drugbank_database/drugbank_files_without_preperation/" drug_sequences/ external_links/ Protein_identifiers/ structure/ target_sequences/ $path_to_project > $output_file

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

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_file.cypher > cypher_output.txt 2>&1

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_rela_file.cypher

