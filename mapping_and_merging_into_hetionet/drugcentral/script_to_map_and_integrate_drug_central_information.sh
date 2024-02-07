#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

license='Attribution-NonCommercial 4.0 International'


now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugcentral product'

python3 mapping_product_drugcentral.py $path_to_project > product/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Durgcentral protein'

python3 mapping_protein_drugcentral.py $path_to_project > protein/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugcentral go'

python3 mapping_GOterm_drugcentral.py $path_to_project > goTerm/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugcentral chemical'

echo "Current time: $now"
python3 mapping_chemical_drugcentral.py $path_to_project > chemical/output.txt


now=$(date +"%F %T")
echo 'integrate Drugcentral pc'

echo "Current time: $now"
python3 mapping_pharmaClass.py $path_to_project > pharmaClass/output.txt


now=$(date +"%F %T")
echo 'integrate Drugcentral atc'

echo "Current time: $now"
python3 mapping_atc_drugcentral.py $path_to_project > atc/output.txt


now=$(date +"%F %T")
echo 'integrate Drugcentral disease'

echo "Current time: $now"
python3 mapping_disease_drugcentral.py $path_to_project > disease/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 60

now=$(date +"%F %T")
echo 'integrate Drugcentral different edges'

echo "Current time: $now"
python3 prepare_direct_edges_from_dc.py $path_to_project > edge/output_directed.txt

now=$(date +"%F %T")
echo 'integrate Drugcentral interaction edges'

echo "Current time: $now"
python3 prepare_interaction_edge.py $path_to_project > edge/output_interacts.txt

now=$(date +"%F %T")
echo 'integrate Drugcentral chemical-product edges'

echo "Current time: $now"
python3 prepare_edge_product_chemical.py $path_to_project > edge/output_edge_to_product.txt

now=$(date +"%F %T")
echo 'integrate Drugcentral chemical-protein edges'

echo "Current time: $now"
python3 merge_protein_chemical_edge.py $path_to_project > edge/output_edge_to_protein.txt


now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 60
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 90

