#!/bin/bash


#path to project
path_to_project=$1

# path to neo4j
path_neo4j=$2

#password
password=$3

echo download omim files if needed
now=$(date +"%F %T")
echo "Current time: $now"
cd data

FILE=genemap2.txt
if [ -f "$FILE" ]; then
    echo "$FILE exist"
else 
    python3 load_omim_files.py
    ./prepare_files.sh
fi

cd ..


echo excecute parser
now=$(date +"%F %T")
echo "Current time: $now"

python3 prepare_nodes_and_relationships.py $path_to_project > output/output.txt


echo integrat into neo4j
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j status

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt
python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

now=$(date +"%F %T")
echo "Current time: $now"

sleep 20
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30
