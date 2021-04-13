#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

python3 importSideEffects_change_to_umls_meddra_final.py data/ $path_to_project > output/output_integration_sider.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate sider into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher > output/output_cypher_integration.txt 2>&1

sleep 60

$path_neo4j/neo4j restart


sleep 120