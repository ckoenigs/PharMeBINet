#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank drugs with interaction into Hetionet'

python integrate_DrugBank_with_interaction_into_hetionet.py > output_integration_file_generation.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file cypher.cypher > output_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

chmod 775 merge_nodes.sh

./merge_nodes.sh > output_merge_compound.txt