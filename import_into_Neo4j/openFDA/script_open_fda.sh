#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

python3 import_openFDA.py '/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/openFDA/' > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate pathway into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/openFDA/load-cypher.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 120