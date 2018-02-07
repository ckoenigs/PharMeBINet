#!/bin/bash

#define path to neo4j bin
#path_neo4j=/home/cassandra/Dokumente/hetionet/neo4j-community-3.1.6/bin
path_neo4j=$1

# sider path
sider_path=$2

# ctd path
ctd_path=$3

# ndf-rt path
ndf_rt_path=$4

# aeolus path
aeolus_path=$5

# DO PATH with obo file
do_path=$6

now=$(date +"%F %T")
echo "Current time: $now"

cd sider 
echo sider

python importSideEffects_change_to_umls_meddra_final.py $sider_path > output_integration_sider.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate sider into neo4j

$path_neo4j/neo4j-shell -file Sider_database_1.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd ctd
echo ctd

python importCTD_final.py $ctd_path > output_integration_ctd.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate ctd into neo4j

for i in {1..3}
do
    echo $i


    $path_neo4j/neo4j-shell -file CTD_database_$i.cypher > output_cypher_integration_$i.txt

    sleep 180

    $path_neo4j/neo4j restart


    sleep 120

done


cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  ndf_rt
echo ndf-rt

python induce_and_contraindication_final.py $ndf_rt_path > output_integration_ndf_rt.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate ndf-rt into neo4j

$path_neo4j/neo4j-shell -file NDF_RT_database_1.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  do
echo do

python ontology_to_neo4j_final.py -i $do_path -s 5 -r [] > output_integration_do.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  hpo
echo hpo

python integrate_hpo_disease_symptomes_into_neo4j.py  > output_integration_hpo.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate hpo into neo4j

$path_neo4j/neo4j-shell -file integrate_hpo_into_neo4j_1.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd aeolus
echo aeolus

python importAeolus_final.py $aeolus_path > output_integration_aeolus.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate aeolus into neo4j

for i in {1..4}
do
    echo $i


    $path_neo4j/neo4j-shell -file CTD_database_$i.cypher > output_cypher_integration_$i.txt

    sleep 180

    $path_neo4j/neo4j restart


    sleep 120

done

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  drugbank
echo drugbank

python transform_drugbank_to_tsv_version_3.py > output_generate_drubank_file.txt


now=$(date +"%F %T")
echo "Current time: $now"

python integrate_drugbank_into_neo4j.py  > output_integration_drugbank.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate drugbank into neo4j

$path_neo4j/neo4j-shell -file DrugBank_database_1.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  EFO
echo EFO

python extract_information_from_efo_and_integrate_into_neo4j.py > output_generate_integration_file.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate efo into neo4j

$path_neo4j/neo4j-shell -file integrate_efo_disease_into_neo4j_1.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  MONDO
echo mondo

python integrate_mondo_into_neo4j.py > output_generate_integration_file.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate mondo into neo4j

$path_neo4j/neo4j-shell -file integrate_mondo_disease_into_neo4j_1.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

now=$(date +"%F %T")
echo "Current time: $now"

python get_hierarchy_mondo_extract.py > output_get_hierarchy_and_cypher_file.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate level into mondo in neo4j

$path_neo4j/neo4j-shell -file integrate_level.cypher > output_cypher_integration_level.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..

now=$(date +"%F %T")
echo "Current time: $now"


