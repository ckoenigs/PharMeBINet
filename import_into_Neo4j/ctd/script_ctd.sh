#!/bin/bash

#path to project
path_to_ctd_data=$1

# path to neo4j
path_neo4j=$2

# password neo4j
password=$3

file=$path_to_ctd_data/ctd_data/CTD_genes.tsv

if [ ! -f "$file" ];
then
    echo download ctd files
    now=$(date +"%F %T")
    echo "Current time: $now"
    echo download files

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


echo nodes
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f cypher/nodes_1.cypher 


sleep 60
python ../../restart_neo4j.py $path_neo4j > neo4j.txt
sleep 60
now=$(date +"%F %T")
echo "Current time: $now"
echo edge

$path_neo4j/cypher-shell -u neo4j -p $password -f cypher/edges_1.cypher 

now=$(date +"%F %T")
echo "Current time: $now"

sleep 60
python ../../restart_neo4j.py $path_neo4j > neo4j.txt
sleep 60

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f cypher/nodes_delete.cypher

now=$(date +"%F %T")
echo "Current time: $now"

sleep 60
python ../../restart_neo4j.py $path_neo4j > neo4j.txt
sleep 60







