#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# path to project
path_to_project=$2

#password
password=$3

# license
license="https://www.ncbi.nlm.nih.gov/home/about/policies/"

now=$(date +"%F %T")
echo "Current time: $now"
echo "snp information for integrated dbSNP nodes"

python3 extract_dbSNP_info_for_integrated_node.py $path_to_project "${license}" > output/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrat dbSNP information into Neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

now=$(date +"%F %T")
echo "Current time: $now"


sleep 30
$path_neo4j/neo4j restart
sleep 30

sleep 60
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo integrat dbSNP clinvar rela

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher


now=$(date +"%F %T")
echo "Current time: $now"
echo integrat dbSNP clinvar rela

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_dbSNP_clinVar.cypher



sleep 30
$path_neo4j/neo4j restart
sleep 30


now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate dbSNP

python3 map_dbSNP_to_nodes.py $path_to_project "${license}" > output_mapping/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo map dbSNP gene

python3 map_dbSNP_gene_to_gene.py $path_to_project  > output_mapping/output_gene.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrat mapping dbSNP information into Neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output_mapping/cypher.cypher

now=$(date +"%F %T")
echo "Current time: $now"

now=$(date +"%F %T")
echo "Current time: $now"
echo map dbSNP gene

python3 integrate_gene_variant_rela.py $path_to_project  > output_mapping/output_gene_variant.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrat mapping edge dbSNP information into Neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output_mapping/cypher_edge.cypher

now=$(date +"%F %T")
echo "Current time: $now"



sleep 30
$path_neo4j/neo4j restart
sleep 60