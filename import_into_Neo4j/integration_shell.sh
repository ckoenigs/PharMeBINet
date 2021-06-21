#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

# import tool
name_of_import_tool='Neo4j-GraphML-Importer-v1.1.5'
echo $name_of_import_tool

now=$(date +"%F %T")
echo "Current time: $now"
echo add hetionet and resource to nodes

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher 


now=$(date +"%F %T")
echo "Current time: $now"

cd sider 
echo sider

./script_sider.sh $path_neo4j $path_to_project > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd bioGrid 
echo bioGrid

./script_biogrid.sh $path_neo4j $path_to_project > output.txt


cd ..



now=$(date +"%F %T")
echo "Current time: $now"


cd  ndf_rt
echo ndf-rt

./script_import_ndf_rt.sh $path_neo4j $path_to_project > output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
cd  med_rt
echo med-rt

./script_med_rt_integration.sh $path_neo4j $path_to_project > output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  do
echo do

./script_import_do.sh $path_neo4j $path_to_project  > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  Uberon
echo Uberon

#download uberon
wget -O data/ext.obo "http://purl.obolibrary.org/obo/uberon/ext.obo"


python3 ../EFO/transform_obo_to_csv_and_cypher_file.py data/ext.obo Uberon uberon_extend $path_to_project > output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate uberon into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output_cypher_integration.txt 2>&1

sleep 60

$path_neo4j/neo4j restart


sleep 120


cd ..


now=$(date +"%F %T")
echo "Current time: $now"


cd  GO
echo go

./script_to_integrate_go.sh $path_neo4j $path_to_project  > output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  hpo
echo hpo

./hpo_integration.sh $path_neo4j $path_to_project > output_hpo.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd aeolus
echo aeolus

./script_aeolus.sh $path_neo4j $path_to_project > output_script.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd uniProt
echo UniProt

./script_uniprot.sh $path_neo4j $path_to_project > output_script.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  drugbank
echo drugbank

./script_to_start_program_and_integrate_into_neo4j.sh $path_to_project $path_neo4j > output_script.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  EFO
echo EFO

#download do
#wget  -O ./efo.obo "https://www.ebi.ac.uk/efo/efo.obo"

# python3 transform_obo_to_csv_and_cypher_file.py efo.obo EFO efo $path_to_project > output_generate_integration_file.txt

# now=$(date +"%F %T")
# echo "Current time: $now"

# echo integrate efo into neo4j

# $path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output_cypher_integration.txt 2>&1

# sleep 60

# $path_neo4j/neo4j restart


# sleep 120

cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  adrecs_target
echo adrecs-target

./script_adrecs_target.sh $path_neo4j $path_to_project > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  ncbi_genes
echo NCBI

./script_ncbi_gene.sh $path_neo4j $path_to_project > output.txt

cd ..


now=$(date +"%F %T")
echo "Current time: $now"

cd  IID
echo IID

./script_iid.sh $path_neo4j $path_to_project > output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  PharmGKB
echo PharmGKB

now=$(date +"%F %T")
echo "Current time: $now"

./script_pharmGKB.sh $path_neo4j $name_of_import_tool > output/script_output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  drugcentral
echo drugcentral

now=$(date +"%F %T")
echo "Current time: $now"

./integrate_drugcentral.sh $path_neo4j $name_of_import_tool > output/script_output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  pathway
echo pathway

./script_pathway.sh $path_neo4j $path_to_project > output.txt

cd ..


now=$(date +"%F %T")
echo "Current time: $now"


cd  reactome
echo reactome

./script_import_recatome_with_graphml.sh $path_neo4j $name_of_import_tool > output_reactome.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  mondo
echo mondo


./new_mondo.sh $path_neo4j $path_to_project > output_integration_of_everything.txt


cd ..


now=$(date +"%F %T")
echo "Current time: $now"

cd  OMIM
echo omim


./script_to_execute_omim.sh $path_to_project $path_neo4j  > output/output_integration_of_everything.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  ClinVar
echo ClinVar

./script_clinvar.sh $path_neo4j $path_to_project  > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd ctd
echo ctd

./script_ctd.sh /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases $path_neo4j > output.txt


cd ..

cd  dbSNP
echo dbSNP

#python3 parse_json_to_tsv_dbsnp.py "/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/dbSNP" $path_to_project  > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate efo into neo4j

#$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output/output_cypher_node.txt 2>&1

sleep 60

$path_neo4j/neo4j restart


sleep 120

cd ..