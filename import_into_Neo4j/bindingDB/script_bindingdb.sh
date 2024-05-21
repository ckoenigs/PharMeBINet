#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


# prepare directories
if [ ! -d output ]; then
  mkdir output
fi
if [ ! -d tsv_from_mysql ]; then
  mkdir tsv_from_mysql
fi
if [ ! -d idx_tsv ]; then
  mkdir idx_tsv
fi
if [ ! -d data ]; then
  mkdir data
fi


now=$(date +"%F %T")
echo "Current time: $now"

echo prepare TSV files

python3 merge_and_save.py $path_to_project > output/output_tsv.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo prepare query files

python3 prepare_queries.py $path_to_project > output/output_cypher.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate bindingDB nodes into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/create_nodes.cypher > output/cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate bindingDB index into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/create_index.cypher > output/cypher2.txt

sleep 20

python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt


sleep 60

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate binding db rela into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/create_edges.cypher > output/cypher.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt


sleep 30


now=$(date +"%F %T")
echo "Current time: $now"