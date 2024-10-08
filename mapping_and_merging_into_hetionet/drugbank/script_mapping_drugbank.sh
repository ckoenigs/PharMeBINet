#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


if [ ! -d output ]; then
  mkdir output
  mkdir compound_interaction
  mkdir compound_pc
  mkdir compound_variant
  mkdir data
  mkdir protein
  mkdir gene_variant
  mkdir metabolite
  mkdir pathway
  mkdir pharmacological_class
  mkdir product
  mkdir reaction
  mkdir rela_protein
  mkdir salts
fi

license='Attribution-NonCommercial 4.0 International'


sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 60

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank drugs with interaction into Hetionet'

python3 integrate_DrugBank_with_interaction_into_hetionet.py "${license}" $path_to_project > compound_interaction/output_integration_file_generation.txt

now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password compound_interaction/cypher.cypher > output/cypher.txt


echo merge
chmod 775 merge_nodes.sh

./merge_nodes.sh $path_neo4j $password > output_merge_compound.txt


sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 30

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank salts with interaction into Hetionet'

python3 salt_to_compound_mapping_connection_to_drugs.py "$license" $path_to_project > salts/output_integration_file_generation_salt.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank product  with rela to compound into Hetionet'

python3 integrate_product_and_rela_to_compound.py "$license" $path_to_project > product/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank gene variant '

python3 mapping_gene_variant_to_variant.py "$license" $path_to_project > gene_variant/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank pathway'

python3 mapping_pathway.py "$license" $path_to_project > pathway/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank metabolite'

python3 mapping_drugbank_metabolite.py "$license" $path_to_project > metabolite/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher1.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 30


now=$(date +"%F %T")
echo "Current time: $now"
echo merge nodes

chmod 775 merge_nodes_salt.sh

./merge_nodes_salt.sh $path_neo4j $password > output/output_merge_compound.txt


sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 30


now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank compound-variant edge'

python3 integrate_variant_compound_edge.py $path_to_project "$license" > gene_variant/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo rela

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_rela.cypher > output/cypher2.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 60


now=$(date +"%F %T")
echo "Current time: $now"
echo delete compounds which did not mapped

python ../../execute_cypher_shell.py $path_neo4j $password cypher_delete_compound.cypher > output/cypher3.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 50



now=$(date +"%F %T")
echo "Current time: $now"
echo 'calculate similarities'

# python3 similarity.py  $path_to_project > compound_interaction/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password compound_interaction/cypher_resemble.cypher > output/cypher4.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 60

now=$(date +"%F %T")
echo "Current time: $now"


