#!/bin/bash

now=$(date +"%F %T")
echo "Current time: $now"
echo integration of chemical-pathways
../../../../../neo4j-community-3.2.9/bin/neo4j-shell -file cypher.cypher > output_cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"
../../../../../neo4j-community-3.2.9/bin/neo4j restart

cd ..
cd chemical_disease
now=$(date +"%F %T")
echo "Current time: $now"
echo integration of chemical-disease
#../../../../../neo4j-community-3.2.9/bin/neo4j-shell -file cypher.cypher > output_cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"
../../../../../neo4j-community-3.2.9/bin/neo4j restart

cd ..
cd gene_disease
now=$(date +"%F %T")
echo "Current time: $now"
echo integration of disease-gene
#../../../../../neo4j-community-3.2.9/bin/neo4j-shell -file cypher.cypher > output_cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"
../../../../../neo4j-community-3.2.9/bin/neo4j restart


now=$(date +"%F %T")
echo "Current time: $now"
#sudo shutdown -h 60
