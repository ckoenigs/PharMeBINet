#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

license='CC BY-NC 4.0'

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank drugs with interaction into Hetionet'

python3 integrate_DrugBank_with_interaction_into_hetionet.py "${license}" $path_to_project > compound_interaction/output_integration_file_generation.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f compound_interaction/cypher.cypher > output_cypher_drug.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo interactions

$path_neo4j/cypher-shell -u neo4j -p test -f compound_interaction/cypher_interaction.cypher > compound_interaction/output_interaction_cypher.txt

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

python3 salt_to_compound_mapping_connection_to_drugs.py "$license" $path_to_project > salts/output_integration_file_generation_salt.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f salts/cypher_salt.cypher > salts/output_salt_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo merge nodes

chmod 775 merge_nodes_salt.sh

./merge_nodes_salt.sh > output/output_merge_compound.txt


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


now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank salts with interaction into Hetionet'

python3 mapping_gene_variant_to_variant.py "$license" $path_to_project > gene_variant/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f gene_variant/cypher.cypher > gene_variant/output_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120


now=$(date +"%F %T")
echo "Current time: $now"
echo 'calculate similarities'

# python3 similarity.py  $path_to_project > compound_interaction/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f compound_interaction/cypher_resemble.cypher > compound_interaction/output_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120



