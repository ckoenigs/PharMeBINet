#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# path to project
path_to_project=$2

now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate gene

python map_CTD_gene_gene_hetionet.py $path_to_project > gene/output_gene.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file gene/cypher.cypher > gene/output_cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"


sleep 180
$path_neo4j/neo4j restart
sleep 120


now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate GO

python integrate_CTD_GO_to_Hetionet.py $path_to_project > GO/output.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file GO/cypher.cypher > GO/output_cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"


sleep 180
$path_neo4j/neo4j restart
sleep 120
now=$(date +"%F %T")
echo "Current time: $now"
echo mapping and integration

python map_CTD_pathways_to_hetionet.py $path_to_project > pathway/output.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file pathway/cypher.cypher > pathway/output_cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"


sleep 180
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate Disease

python integrate_and_map_CTD_disease_to_Hetionet_disease_new.py $path_to_project > disease_Disease/output_new.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file disease_Disease/cypher.cypher > disease_Disease/output_cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"


sleep 180
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate chemical

python integration_CTD_chemicals_into_hetionet.py > chemical/output.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file chemical/cypher.cypher > chemical/output_cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"


sleep 180
$path_neo4j/neo4j restart
sleep 120


#############################################################################################################################
# integration of the different relationships


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate gene-particitates-pathway

python integrate_gene_participat_pathway.py $path_to_project > gene_pathway/output.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file gene_pathway/cypher.cypher > gene_pathway/output_cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"


sleep 180
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate gene-particitates-go

python integrate_gene_participates_GO.py $path_to_project > gene_go/output.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file gene_go/cypher.cypher > gene_go/output_cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"
exit 1


sleep 180
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate go-associate-disease

python integrate_disease_go.py $path_to_project > disease_go/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file disease_go/cypher.cypher > disease_go/output_cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"



sleep 180
$path_neo4j/neo4j restart
sleep 120


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate disease-associates-pathway

python integrate_disease_associates_pathway.py $path_to_project > disease_pathway/output.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file disease_pathway/cypher.cypher > disease_pathway/output_cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"


sleep 180
$path_neo4j/neo4j restart
sleep 120


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate disease-associates-gene

python integrate_disease_gene.py $path_to_project > gene_disease/output.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file gene_disease/cypher.cypher > gene_disease/output_cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"


sleep 180
$path_neo4j/neo4j restart
sleep 120


# sudo shutdown -h 60 # fährt das system in 60 min
