#!/bin/bash

#path to project
path_to_project=$1

echo download ctd files
now=$(date +"%F %T")
echo "Current time: $now"

#python download_the_ctd_files.py > output_download.txt


echo first remove the first lines of the ctd files
now=$(date +"%F %T")
echo "Current time: $now"
cd ctd_data

#for i in *.csv; do 
#    ./delete_the_head.sh $i
#done

cd ..

echo python
now=$(date +"%F %T")
echo "Current time: $now"

python integrate_whole_CTD_into_neo4j_with_csv.py $path_to_project > output_integration.txt

now=$(date +"%F %T")
echo "Current time: $now"

cd cypher

echo nodes
now=$(date +"%F %T")
echo "Current time: $now"

../../../../../neo4j-community-3.2.9/bin/neo4j-shell -file nodes_1.cypher > output_nodes_1.txt

echo edges 
now=$(date +"%F %T")
echo "Current time: $now"

sleep 180
../../../../../neo4j-community-3.2.9/bin/neo4j restart
sleep 120
now=$(date +"%F %T")
echo "Current time: $now"

../../../../../neo4j-community-3.2.9/bin/neo4j-shell -file edges_1.cypher > output_edges_1.txt

now=$(date +"%F %T")
echo "Current time: $now"

sleep 180
../../../../../neo4j-community-3.2.9/bin/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"

../../../../../neo4j-community-3.2.9/bin/neo4j-shell -file nodes_delete.cypher > output_delete_nodes.txt

now=$(date +"%F %T")
echo "Current time: $now"

sleep 180
../../../../../neo4j-community-3.2.9/bin/neo4j restart
sleep 120

cd ..

echo remove csv and csv.gz files
#rm ctd_data/*.csv*





