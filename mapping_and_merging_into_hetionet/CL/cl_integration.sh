#!/bin/bash

path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


if [ ! -d output ]; then
  mkdir output
  mkdir go
fi

python3 Add_Cell_line.py $path_to_project > output/output_add.txt


echo map protein
now=$(date +"%F %T")
echo "Current time: $now"

python3 map_cl_to_anatomy.py $path_to_project > output/output_map_anatomy.txt


echo map protein
now=$(date +"%F %T")
echo "Current time: $now"

python3 map_CL_to_go.py $path_to_project > go/output_map.txt

echo integrate connection with ne4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt

sleep 40

echo add edges
now=$(date +"%F %T")
echo "Current time: $now"

python3 CL_edges.py $path_to_project > go/output_map.txt


python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt
sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt

sleep 40