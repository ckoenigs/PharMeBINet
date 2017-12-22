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



