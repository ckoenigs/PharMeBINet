#!/bin/bash

path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

# prepare directories
if [ ! -d output ]; then
  mkdir output
  mkdir mapping
fi

now=$(date +"%F %T")
echo "Current time: $now"
echo start mapping and prepare cypher, csv and bash shell

python3 change_identifier_from_DO_to_MONDO_with_monarch_source.py $path_to_project > output/output_mapping_preperation.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate mondo

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30

now=$(date +"%F %T")
echo "Current time: $now"
chmod 775 merge_nodes.sh

./merge_nodes.sh $path_neo4j > output/output_mergy.txt

sleep 20

python ../../restart_neo4j.py $path_neo4j > output/neo41.txt

sleep 30

now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_end.cypher > output/cypher2.txt

sleep 20

python ../../restart_neo4j.py $path_neo4j > output/neo42.txt

sleep 30



