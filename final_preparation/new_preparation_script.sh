#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# define import tool
import_tool=$2

# define import tool
password=$3

# path to pharMeBiNet graphml
path_to_pharMeBiNet='/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/PharMeBiNet/'

sleep 60

python ../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo 'export database'

python ../execute_cypher_shell.py $path_neo4j $password export_pharMeBINet.cypher > output/cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"

sleep 60

python ../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 120



now=$(date +"%F %T")
echo "Current time: $now"
echo 'prepare graphML import with index'

python3 prepare_shell_for_graphml_import.py > output/output_preparation_graphml_import.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'remove not used data'

python3 prepare_graphML_pharmebinet.py > output/output_preparation.txt



now=$(date +"%F %T")
echo "Current time: $now"

sleep 120

$path_neo4j/restart_neo4j.sh pharmebinet restart

sleep 60

chmod 775 shell_import_pharmebinet.sh

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate used data'

./shell_import_pharmebinet.sh $import_tool $path_to_pharMeBiNet $password > output/import_graphml.txt

sleep 120

python ../restart_neo4j.py $path_neo4j > output/neo4.txt

sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
