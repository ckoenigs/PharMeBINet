#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate proteins with interaction into Hetionet'

python integrate_into_hetionet_with_extra_rela_without_ctd.py > output_integration_file_generation.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo node cypher

$path_neo4j/neo4j-shell -file cypher_node.cypher > output_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo rela cypher

$path_neo4j/neo4j-shell -file cypher_rela.cypher > output_cypher_rela.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120