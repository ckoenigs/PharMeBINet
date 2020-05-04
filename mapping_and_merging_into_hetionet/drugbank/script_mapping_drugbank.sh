#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

license='CC BY-NC 4.0'

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank drugs with interaction into Hetionet'

python3 integrate_DrugBank_with_interaction_into_hetionet.py "${license}" $path_to_project > output_integration_file_generation.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output_cypher_drug.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo interactions

$path_neo4j/cypher-shell -u neo4j -p test -f compound_interaction/cypher_interaction.cypher > output_interaction_cypher.txt

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

python3 salt_to_compound_mapping_connection_to_drugs.py "$license" $path_to_project > output_integration_file_generation_salt.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_salt.cypher > output_salt_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo merge nodes

chmod 775 merge_nodes_salt.sh

./merge_nodes_salt.sh > output_merge_compound.txt


sleep 180
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo delete compounds which did not mapped

#$path_neo4j/cypher-shell -u neo4j -p test -f cypher_delete_compound.cypher > output_delete_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120
