#!/bin/bash

#path to project
path_to_ctd_data=$1

# path to neo4j
path_neo4j=$2

# password neo4j
password=$3



# prepare directories
if [ ! -d output ]; then
  mkdir output
fi

if [ ! -d cypher ]; then
  mkdir cypher
fi


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

python ../../execute_cypher_shell.py $path_neo4j $password cypher/nodes_1.cypher > output/cypher.txt

sleep 60
python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt
sleep 60
now=$(date +"%F %T")
echo "Current time: $now"
echo edge

python ../../execute_cypher_shell.py $path_neo4j $password cypher/edges_1.cypher > output/cypher1.txt

now=$(date +"%F %T")
echo "Current time: $now"

sleep 60
python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt
sleep 60

now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password cypher/nodes_delete.cypher > output/cypher2.txt

now=$(date +"%F %T")
echo "Current time: $now"

sleep 60
python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt
sleep 60







