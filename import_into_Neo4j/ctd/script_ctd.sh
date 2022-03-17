#!/bin/bash

#path to project
path_to_ctd_data=$1

# path to neo4j
path_neo4j=$2

file=$path_to_ctd_data/ctd_data/CTD_genes.tsv

if [ ! -f "$file" ];
then
    echo download ctd files
    now=$(date +"%F %T")
    echo "Current time: $now"

    # download gene-disease manual because there is a human check!

    python3 download_the_ctd_files.py $path_to_ctd_data > output_download.txt


    echo first remove the first lines of the ctd files
    now=$(date +"%F %T")
    echo "Current time: $now"
    # cd path_to_ctd_data/ctd_data

    for i in $path_to_ctd_data/ctd_data/*.tsv; do
      $path_to_ctd_data/ctd_data/delete_the_head.sh $i
    done

    #cd ..
fi

echo prepare ctd data
now=$(date +"%F %T")
echo "Current time: $now"

python3 integrate_whole_CTD_into_neo4j_with_tsv.py $path_to_ctd_data True > output_integration.txt

now=$(date +"%F %T")
echo "Current time: $now"

cd cypher

echo nodes
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f nodes_1.cypher 


sleep 60
$path_neo4j/neo4j restart
sleep 120
now=$(date +"%F %T")
echo "Current time: $now"
echo edge

$path_neo4j/cypher-shell -u neo4j -p test -f edges_1.cypher 

now=$(date +"%F %T")
echo "Current time: $now"

sleep 120
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f nodes_delete.cypher

now=$(date +"%F %T")
echo "Current time: $now"

sleep 120
$path_neo4j/neo4j restart
sleep 120

cd ..






