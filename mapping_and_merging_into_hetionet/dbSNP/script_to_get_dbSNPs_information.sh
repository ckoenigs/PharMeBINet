#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# path to project
path_to_project=$2

#password
password=$3

# path to data
path_to_data=$4

# license
license="https://www.ncbi.nlm.nih.gov/home/about/policies/"


sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30

now=$(date +"%F %T")
echo "Current time: $now"
echo "snp information for integrated dbSNP nodes"

python3 extract_dbSNP_info_for_integrated_node.py $path_to_project "${license}" $path_to_data > output/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrat dbSNP information into Neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"


sleep 60
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 180

sleep 60
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 180



now=$(date +"%F %T")
echo "Current time: $now"
echo integrat dbSNP edges

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrat dbSNP clinvar rela

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_dbSNP_clinVar.cypher > output/cypher3.txt


sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt
sleep 60


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

python ../../execute_cypher_shell.py $path_neo4j $password output_mapping/cypher.cypher > output/cypher4.txt

now=$(date +"%F %T")
echo "Current time: $now"

now=$(date +"%F %T")
echo "Current time: $now"
echo map dbSNP gene

python3 integrate_gene_variant_rela.py $path_to_project  > output_mapping/output_gene_variant.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrat mapping edge dbSNP information into Neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output_mapping/cypher_edge.cypher > output/cypher5.txt

now=$(date +"%F %T")
echo "Current time: $now"



sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j2.txt

sleep 60
