#!/bin/bash

#define path to neo4j bin
#path_neo4j=/home/cassandra/Dokumente/hetionet/neo4j-community-3.1.6/bin
path_neo4j=$1

now=$(date +"%F %T")
echo "Current time: $now"
echo add hetionet and resource to nodes

$path_neo4j/neo4j-shell -file cypher.cypher > output_cypher_integration.txt


now=$(date +"%F %T")
echo "Current time: $now"

cd sider 
echo sider

python importSideEffects_change_to_umls_meddra_final.py > output_integration_sider.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate sider into neo4j

$path_neo4j/neo4j-shell -file cypher.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd ctd
echo ctd

./script_ctd.sh > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  ndf_rt
echo ndf-rt

python prepare_ndf_rt_to_neo4j_integration.py $ndf_rt_path > output_integration_ndf_rt.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate ndf-rt into neo4j

$path_neo4j/neo4j-shell -file cypher_file.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120
echo delete ndf-rt nodes without relaionships

$path_neo4j/neo4j-shell -file cypher_file_delete.cypher > output_cypher_delete.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  do
echo do

python ../EFO/transform_obo_to_csv_and_cypher_file.py data/HumanDO.obo do diseaseontology > output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate do into neo4j

cat cypher.cypher | $path_neo4j/cypher-shell -u neo4j -p test > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120


cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  hpo
echo hpo

#python integrate_hpo_disease_symptomes_into_neo4j.py  > output_integration_hpo.txt
python ../EFO/transform_obo_to_csv_and_cypher_file.py hpo.obo hpo HPOsymptom > output_generate_integration_file.txt

echo generation of csv from tsv file
python integrate_hpo_disease_symptomes_into_neo4j.py > output_disease.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate hpo into neo4j

cat cypher.cypher | $path_neo4j/cypher-shell -u neo4j -p test > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd aeolus
echo aeolus

python importAeolus_final.py aeolus_v1/ > output_integration_aeolus.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate aeolus into neo4j

$path_neo4j/neo4j-shell -file cypher.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd uniProt
echo UniProt

python parse_uniprot_flat_file_to_tsv.py database/uniprot_sprot.dat > output_integration.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate aeolus into neo4j

$path_neo4j/neo4j-shell -file cypher_protein.cypher > output_cypher_integration_$i.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  drugbank
echo drugbank

./script_to_start_program_and_integrate_into_neo4j.sh > output_script.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  EFO
echo EFO

python transform_obo_to_csv_and_cypher_file.py efo.obo EFO EFOdisease > output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate efo into neo4j

cat cypher.cypher | $path_neo4j/cypher-shell -u neo4j -p test > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..


now=$(date +"%F %T")
echo "Current time: $now"

cd  ncbi_genes
echo NCBI

python integrate_ncbi_genes_which_are_already_in_hetionet.py > output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate ncbi into neo4j

$path_neo4j/neo4j-shell -file cypher_node.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  mondo
echo mondo


./integrate_mondo_and_add_level.sh $path_neo4j /home/cassandra/Dokumente/neo4j-community-3.5.8/data/databases/restart_neo4j.sh > output_integration_of_everything.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"


