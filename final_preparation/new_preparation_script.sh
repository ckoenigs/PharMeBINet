#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# define import tool
import_tool='../import_into_Neo4j/Neo4j-GraphML-Importer-v1.1.5'

# path to pharMeBiNet graphml
path_to_pharMeBiNet='/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/PharMeBiNet/'

now=$(date +"%F %T")
echo "Current time: $now"
echo 'export database'

$path_neo4j/cypher-shell -u neo4j -p test -f export_pharMeBINet.cypher

now=$(date +"%F %T")
echo "Current time: $now"

sleep 60

$path_neo4j/neo4j restart


sleep 120


now=$(date +"%F %T")
echo "Current time: $now"
echo 'remove not used data'

python3 prepare_graphML_pharmebinet.py > output/output_preparation.txt


sleep 120

$path_neo4j/restart_neo4j.sh pharmebinet restart

sleep 60

chmod 775 shell_import_pharmebinet.sh

./shell_import_pharmebinet.sh $import_tool $path_to_pharMeBiNet > output/import_graphml.txt

sleep 60

$path_neo4j/neo4j restart

sleep 120

now=$(date +"%F %T")
echo "Current time: $now"