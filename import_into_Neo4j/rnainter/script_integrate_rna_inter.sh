#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

echo $path_to_project

now=$(date +"%F %T")
echo "Current time: $now"

file=data/Download_data_RR.tar.gz
# download data only if not a file exists
if [ ! -f "$file" ];
then

    file_Array=( "Download_data_RR.tar.gz" "Download_data_RP.tar.gz" "Download_data_RD.tar.gz" "Download_data_RC.tar.gz" "Download_data_RH.tar.gz")

    #download data 
    for file in ${file_Array[*]}; do
        echo $file
        wget  -O "data/"$file "www.rnainter.org/raidMedia/download/"$file
    done
fi


python3 import_rnainter.py $path_to_project "Homo sapiens" > output/output.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate rnaInter into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 60

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate rnaInter into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 60