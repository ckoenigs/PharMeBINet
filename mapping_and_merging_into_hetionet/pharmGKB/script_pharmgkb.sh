#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

license="CC BY-SA 4.0"

now=$(date +"%F %T")
echo "Current time: $now"
echo 'map pahrmgkb gene'

python3 map_gene.py $path_to_project > gene/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'map chemical'

python3 map_drug_chemical.py $path_to_project > chemical/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'map variant and haplotypes'

python3 map_haplotype_and_variant.py $path_to_project > variant/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'map phenotypes'

python3 map_phenotype.py $path_to_project $license > disease/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher 

sleep 180
$path_neo4j/neo4j restart
sleep 120


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

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_edge.cypher 

sleep 180
$path_neo4j/neo4j restart
sleep 120
