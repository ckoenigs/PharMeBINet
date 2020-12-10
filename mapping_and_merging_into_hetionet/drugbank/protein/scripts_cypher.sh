#!/bin/bash
now=$(date +"%F %T")
echo "Current time: $now"

echo integrate the proteins

../../../../../neo4j-community-3.2.9/bin/neo4j-shell -file cypher_protein.cypher 
now=$(date +"%F %T")
echo "Current time: $now"

echo integrate rela has component
../../../../../neo4j-community-3.2.9/bin/neo4j-shell -file cypher_protein_rela.cypher

now=$(date +"%F %T")
echo "Current time: $now"