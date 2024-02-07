#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#password
password=$2

#python3 import_openFDA.py '/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/openFDA/' > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate pathway into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/openFDA/load-cypher.cypher > output/cypher.txt

sleep 60

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 60

python ../../execute_cypher_shell.py $path_neo4j $password /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/openFDA/load-cypher-edge.cypher > output/cypher2.txt

sleep 60

$path_neo4j/neo4j restart


sleep 60