#!/bin/bash

#projekt path
path_to_project=$1

# path to neo4j
path_neo4j=$2

# path to drugbank
path_to_drugbank_data="/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/Drugbank_database/drugbank_files_without_preperation/"


echo  $path_neo4j

now=$(date +"%F %T")
echo "Current time: $now"
echo prepare drugbank categories

# python3 update_drugbank_categories.py > out_categories.txt



now=$(date +"%F %T")
echo "Current time: $now"
echo extract sdf information

cd sdf

#./script_sdf.sh $path_to_drugbank_data > output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo information extraction from xml

python3 transform_drugbank_to_tsv.py $path_to_project > output_transform.txt



now=$(date +"%F %T")
echo "Current time: $now"
echo file preperation

output_file=output_file_preperation.txt

python3 file_preperation.py $path_to_drugbank_data drug_sequences/ external_links/ Protein_identifiers/ structure/ target_sequences/ $path_to_project > $output_file

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

$path_neo4j/cypher-shell -u neo4j -p test -f ../cypher_atc.cypher

