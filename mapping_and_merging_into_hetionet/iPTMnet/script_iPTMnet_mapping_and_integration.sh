#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# path to project
path_to_project=$2

#password
password=$3




now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate proteins

if [ ! -d protein ]; then
  mkdir protein
fi

python3 mapping_protein_iptmnet.py $path_to_project > protein/output_protein.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo restarting neo4j

sleep 20
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 20

now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate ptms

if [ ! -d ptm ]; then
  mkdir ptm
fi

python3 mapping_ptm_iptmnet.py $path_to_project > ptm/output_ptm.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo restarting neo4j

sleep 20
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 20


now=$(date +"%F %T")
echo "Current time: $now"
echo 'Edge iPTMnet ptm-protein'

if [ ! -d ptm_protein_edge ]; then
  mkdir ptm_protein_edge
fi

#python3 mapping_ptm_protein_iPTMnet.py $path_to_project > ptm_protein_edge/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate edges into neo4j

#python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher_edge.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo restarting neo4j

sleep 10
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 10

