#!/bin/bash

path_neo4j=$1

#path to project
path_to_project=$2

now=$(date +"%F %T")
echo "Current time: $now"
echo start mapping and prepare cypher, csv and bash shell

python3 change_identifier_from_DO_to_MONDO_with_monarch_source.py $path_to_project > output/output_mapping_preperation.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate mondo

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher > output/output_cypher_integration.txt

sleep 120

$path_neo4j/neo4j restart


sleep 120

chmod 775 merge_nodes.sh

./merge_nodes.sh > output_mergy.txt

sleep 120

$path_neo4j/neo4j restart

sleep 120

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_end.cypher > output/output_cypher_end_integration.txt



