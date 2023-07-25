#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

rm output/cypher.cypher


now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map bioGrid gene'

python3 mapping_gene_bioGrid.py $path_to_project > gene/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map bioGrid chemical'

python3 map_chemical_biogrid.py $path_to_project > chemical/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map bioGrid disease'

python3 mapping_disease_biogrid.py $path_to_project > disease/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map bioGrid chemical'

python3 map_go_bioGrid.py $path_to_project > GO/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 30
$path_neo4j/neo4j restart
sleep 60



now=$(date +"%F %T")
echo "Current time: $now"
echo 'Merge ppi'

python3 merge_ppi.py $path_to_project > interaction/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'Merge biogrid protein-chemical'

python3 merge_protein_chemical_interaction.py $path_to_project > interaction/output_c_p.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate rela into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher

sleep 30
$path_neo4j/neo4j restart
sleep 60
sleep 30
$path_neo4j/neo4j restart
sleep 60
