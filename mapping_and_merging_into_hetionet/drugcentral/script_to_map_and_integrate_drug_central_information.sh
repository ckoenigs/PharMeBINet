#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

license='Attribution-NonCommercial 4.0 International'


now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugcentral product'

python3 mapping_product_drugcentral.py $path_to_project > product/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Durgcentral protein'

python3 mapping_protein_drugcentral.py $path_to_project > protein/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugcentral go'

python3 mapping_GOterm_drugcentral.py $path_to_project > goTerm/output.txt


now=$(date +"%F %T")
echo 'integrate Drugcentral chemical'

echo "Current time: $now"
python3 mapping_chemical_drugcentral.py $path_to_project > chemical/output.txt


now=$(date +"%F %T")
echo 'integrate Drugcentral atc'

echo "Current time: $now"
python3 mapping_atc_drugcentral.py $path_to_project > atc/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher

sleep 120
$path_neo4j/neo4j restart
sleep 120

