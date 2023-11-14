#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

now=$(date +"%F %T")
echo "Current time: $now"
echo parse dbSNP


python3 parse_json_to_tsv_dbsnp.py "/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/dbSNP" $path_to_project  > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate efo into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f cypher.cypher > output/output_cypher_node.txt 2>&1

sleep 60

python ../../restart_neo4j.py $path_neo4j > neo4j.txt

sleep 120