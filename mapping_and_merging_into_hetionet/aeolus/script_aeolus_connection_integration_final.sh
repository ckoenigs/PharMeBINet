#!/bin/bash

path_neo4j=$1

echo Aeolus connection
now=$(date +"%F %T")
echo "Current time: $now"

for i in {1..22}
do
	$path_neo4j/neo4j-shell -file cypher_map/map_connection_of_aeolus_in_hetionet_$i.cypher > outcome_aeolus_connection_$i_cypher.txt
	now=$(date +"%F %T")
	echo "Current time: $now"
	
	$path_neo4j/neo4j restart
	sleep 120
done
now=$(date +"%F %T")
echo "Current time: $now"
