#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

$path_neo4j/restart_neo4j.sh reactome restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo 'extract as property types'

python3 get_property_types.py > output/output_preparation.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'extract as graphml'

$path_neo4j/cypher-shell -u neo4j -p test -f export_cypher.cypher
sleep 180

$path_neo4j/neo4j restart


sleep 120

$path_neo4j/restart_neo4j.sh graph restart

now=$(date +"%F %T")
echo "Current time: $now"
echo 'replace labels'

python3 prepareCsv.py $path_to_project  > output/output_preparation.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'import as graphml'

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher

sleep 180

$path_neo4j/neo4j restart


sleep 120




