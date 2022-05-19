#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2


#download obo file
wget  -O data/hpo.obo "http://purl.obolibrary.org/obo/hp.obo"

#download phenotype_annotation file
# wget -O ./phenotype_annotation.tab "http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/misc/phenotype_annotation.tab"
wget -O data/phenotype.hpoa "http://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa"

# seperate version from content in phenotype
cd data
./delete_head.sh phenotype.hpoa

cd ..

#python3 integrate_hpo_disease_symptomes_into_neo4j.py  > output_integration_hpo.txt
python3 ../EFO/transform_obo_to_tsv_and_cypher_file.py data/hpo.obo hpo HPO_symptom $path_to_project > output/output_generate_integration_file.txt

echo generation of csv from tsv file
python3 integrate_hpo_disease_symptomes_into_neo4j.py $path_to_project > output/output_disease.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate hpo into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher 

sleep 60

$path_neo4j/neo4j restart


sleep 120