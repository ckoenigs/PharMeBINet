#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

license="CC BY-SA 4.0"


# prepare directories
if [ ! -d output ]; then
  mkdir output
  mkdir disease
  mkdir chemical
  mkdir annotation_variant_edge
  mkdir gene
  mkdir metadata_edge
  mkdir pathway
  mkdir variant
  mkdir variant_gene
fi

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

python3 map_haplotype_and_variant.py $path_to_project "${license}" > variant/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'map phenotypes'

python3 map_phenotype.py $path_to_project "${license}" > disease/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30
