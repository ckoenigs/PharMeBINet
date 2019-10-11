#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

license='CC BY-NC 4.0'

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank drugs with interaction into Hetionet'

python integrate_DrugBank_with_interaction_into_hetionet.py $license > output_integration_file_generation.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file cypher.cypher > output_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo interactions

$path_neo4j/neo4j-shell -file compound_interaction/cypher_interaction.cypher > output_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

chmod 775 merge_nodes.sh

./merge_nodes.sh > output_merge_compound.txt


sleep 180
$path_neo4j/neo4j restart
sleep 120


now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank salts with interaction into Hetionet'

python salt_to_compound_mapping_connection_to_drugs.py $license > output_integration_file_generation_salt.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file cypher_salt.cypher > output_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

chmod 775 merge_nodes_salt.sh

./merge_nodes_salt.sh > output_merge_compound.txt


sleep 180
$path_neo4j/neo4j restart
sleep 120