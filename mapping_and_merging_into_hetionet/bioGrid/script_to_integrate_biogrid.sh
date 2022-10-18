#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

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
echo 'Map bioGrid chemical'

python3 map_go_bioGrid.py $path_to_project > GO/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher 

sleep 120
$path_neo4j/neo4j restart
sleep 180

