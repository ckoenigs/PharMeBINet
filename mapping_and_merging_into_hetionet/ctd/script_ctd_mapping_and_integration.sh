#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# path to project
path_to_project=$2

now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate gene

python3 map_CTD_gene_gene_hetionet.py $path_to_project > gene/output_gene.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate GO

python3 integrate_CTD_GO_to_Hetionet.py $path_to_project > GO/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo mapping and integration pathway

python3 map_CTD_pathways_to_hetionet.py $path_to_project > pathway/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate Disease

python3 integrate_and_map_CTD_disease_to_Hetionet_disease_new.py $path_to_project > disease_Disease/output_new.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate chemical

python3 integration_CTD_chemicals_into_hetionet.py $path_to_project > chemical/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate nodes into database

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher 

now=$(date +"%F %T")
echo "Current time: $now"


sleep 60
$path_neo4j/neo4j restart
sleep 120


#############################################################################################################################
# integration of the different relationships


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate gene-particitates-pathway

python3 integrate_gene_participat_pathway.py $path_to_project > gene_pathway/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate gene-particitates-go

# python3 integrate_gene_participates_GO.py $path_to_project > gene_go/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate chemical disease

python3 integration_chemical_disease.py $path_to_project > chemical_disease/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate chemical gene

python3 integration_chemical_gene.py $path_to_project > chemical_gene/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate chemical phenotype


python3 integration_chemical_phenotype.py $path_to_project > chemical_phenotype/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate disease-associates-gene

python3 integrate_disease_gene.py $path_to_project > gene_disease/output.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_edge.cypher

now=$(date +"%F %T")
echo "Current time: $now"

sleep 60
$path_neo4j/neo4j restart
sleep 120



# I decide to not include only association which comes from linked information, but maybe they can be used to compare somtimes??
#now=$(date +"%F %T")
#echo "Current time: $now"
#echo integrate go-associate-disease

#python3 integrate_disease_go.py $path_to_project > disease_go/output.txt


#now=$(date +"%F %T")
#echo "Current time: $now"

#$path_neo4j/cypher-shell -u neo4j -p test -f disease_go/cypher.cypher > disease_go/output_cypher.txt

#now=$(date +"%F %T")
#echo "Current time: $now"

#sleep 180
#$path_neo4j/neo4j restart
#sleep 120


#now=$(date +"%F %T")
#echo "Current time: $now"
#echo integrate disease-associates-pathway

#python3 integrate_disease_associates_pathway.py $path_to_project > disease_pathway/output.txt

#now=$(date +"%F %T")
#echo "Current time: $now"

#$path_neo4j/cypher-shell -u neo4j -p test -f disease_pathway/cypher.cypher > disease_pathway/output_cypher.txt

#now=$(date +"%F %T")
#echo "Current time: $now"


#sleep 180
#$path_neo4j/neo4j restart
#sleep 120


#now=$(date +"%F %T")
#echo "Current time: $now"
#echo integrate chemical-associates-pathway

#python3 integrate_chemical_pathway.py $path_to_project > chemical_pathway/output.txt

#now=$(date +"%F %T")
#echo "Current time: $now"

#$path_neo4j/cypher-shell -u neo4j -p test -f chemical_pathway/cypher.cypher > chemical_pathway/output_cypher.txt

#now=$(date +"%F %T")
#echo "Current time: $now"


#sleep 180
#$path_neo4j/neo4j restart
#sleep 120



#now=$(date +"%F %T")
#echo "Current time: $now"
#echo integrate chemical-associates-go

#python3 integration_chemical_go.py $path_to_project > chemical_pathway/output.txt

#now=$(date +"%F %T")
#echo "Current time: $now"

#$path_neo4j/cypher-shell -u neo4j -p test -f chemical_go/cypher.cypher > chemical_go/output_cypher.txt

#now=$(date +"%F %T")
#echo "Current time: $now"


#sleep 180
#$path_neo4j/neo4j restart
#sleep 120

# sudo shutdown -h 60 # fährt das system in 60 min
