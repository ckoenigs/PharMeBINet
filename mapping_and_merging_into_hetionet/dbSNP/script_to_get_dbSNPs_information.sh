#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# path to project
path_to_project=$2

# license
license="https://www.ncbi.nlm.nih.gov/home/about/policies/"

now=$(date +"%F %T")
echo "Current time: $now"
echo "snp information for integrated dbSNP nodes"

python3 extract_dbSNP_info_for_integrated_node.py $path_to_project $license > output/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrat dbSNP information into Neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher > output/output_cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"


sleep 120
$path_neo4j/neo4j restart
sleep 120


now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate dbSNP

python3 map_dbSNP_to_nodes.py $path_to_project $license > output_mapping/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrat mapping dbSNP information into Neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f output_mapping/cypher.cypher > output_mapping/output_cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"


sleep 120
$path_neo4j/neo4j restart
sleep 120