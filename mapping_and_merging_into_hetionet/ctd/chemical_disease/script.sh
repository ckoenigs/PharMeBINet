#!/bin/bash

path_neo4j=../../../../../neo4j-community-3.2.9
now=$(date +"%F %T")
echo "Current time: $now"
echo change relationships

#$path_neo4j/bin/neo4j-shell -file queries_to_order.cypher > output_15_cypher_order.txt

sleep 180
#$path_neo4j/bin/neo4j restart
sleep 120

cd ..
now=$(date +"%F %T")
echo "Current time: $now"
echo chemical_disease

#python integration_chemical_disease.py > chemical_disease/output_17_08.txt

cd chemical_disease

now=$(date +"%F %T")
echo "Current time: $now"
echo integration new or update relationships ctd

#$path_neo4j/bin/neo4j-shell -file cypher.cypher > output_17_08_cypher.txt

sleep 180
$path_neo4j/bin/neo4j restart
sleep 120

cd ..
cd gene_disease

now=$(date +"%F %T")
echo "Current time: $now"
echo integration new or update relationships ctd gene_disease

$path_neo4j/bin/neo4j-shell -file cypher.cypher > output_31_08_cypher.txt

sleep 180
$path_neo4j/bin/neo4j restart
sleep 120


cd ..
now=$(date +"%F %T")
echo "Current time: $now"
echo chemical_pathway

python integration_chemical_pathway.py > chemical_pathway/output_31_08.txt

cd chemical_pathway

now=$(date +"%F %T")
echo "Current time: $now"
echo integration new or update relationships ctd chemical_pathway

$path_neo4j/bin/neo4j-shell -file cypher.cypher > output_31_08_cypher.txt

sleep 180
$path_neo4j/bin/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo chemical_go

python integration_chemical_go.py > chemical_go/output_31_08.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo herunterfahren

sudo shutdown -h now

