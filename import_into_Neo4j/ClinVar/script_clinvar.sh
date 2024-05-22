#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

# path to clinvar saved data
path_to_clinvar_data=$3

#password
password=$4


# prepare directories
if [ ! -d output ]; then
  mkdir output
fi
if [ ! -d $path_to_clinvar_data/clinvar ]; then
  mkdir $path_to_clinvar_data/clinvar
fi

now=$(date +"%F %T")
echo "Current time: $now"
echo prepare clinvar data

python3 transform_xml_to_nodes_and_edges.py $path_to_clinvar_data > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate clinvar into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_file_node.cypher > output/cypher.txt

sleep 60

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt

sleep 120

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_file_edges.cypher > output/cypher1.txt

sleep 60

python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt

sleep 60


