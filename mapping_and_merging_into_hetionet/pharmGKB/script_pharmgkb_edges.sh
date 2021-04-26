#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

license="CC BY-SA 4.0"


now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate gene-variant rela'

python3 integrate_variant_to_gene_connection.py $path_to_project $license > variant_gene/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate clinical meta data rela'

python3 integrate_clinical_annotation_metadata.py $path_to_project $license > metadata_edge/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate clinical variant annotation rela'

python3 integrate_different_annotations.py $path_to_project $license > annotation_variant_edge/output.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_edge.cypher 

sleep 120
$path_neo4j/neo4j restart
sleep 120