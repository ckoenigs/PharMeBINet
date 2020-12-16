#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

echo $path_to_project

now=$(date +"%F %T")
echo "Current time: $now"
echo add hetionet and resource to nodes

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output_cypher_integration.txt 2>&1


now=$(date +"%F %T")
echo "Current time: $now"

cd sider 
echo sider

python3 importSideEffects_change_to_umls_meddra_final.py data/ $path_to_project > output_integration_sider.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate sider into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output_cypher_integration.txt 2>&1

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd ctd
echo ctd

./script_ctd.sh $path_to_project $path_neo4j > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  ndf_rt
echo ndf-rt

python3 prepare_ndf_rt_to_neo4j_integration.py $path_to_project > output_integration_ndf_rt.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate ndf-rt into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_file.cypher > output_cypher_integration.txt 2>&1

sleep 180

$path_neo4j/neo4j restart


sleep 120
echo delete ndf-rt nodes without relaionships

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_file_delete.cypher > output_cypher_delete.txt 2>&1

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..

cd  med_rt
echo med-rt

python3 parse_med_rt_to_csv.py $path_to_project > output_integration_ndf_rt.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate med-rt into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_med.cypher > output_cypher_integration.txt 2>&1

sleep 180

$path_neo4j/neo4j restart


sleep 120
echo delete med-rt nodes without relaionships

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_delete.cypher

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  do
echo do

#download do
wget  -O data/HumanDO.obo "https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/main/src/ontology/doid.obo"


python3 ../EFO/transform_obo_to_csv_and_cypher_file.py data/HumanDO.obo do diseaseontology $path_to_project > output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate do into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output_cypher_integration.txt 2>&1

sleep 180

$path_neo4j/neo4j restart


sleep 120


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

echo integrate do into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output_cypher_integration.txt 2>&1

sleep 180

$path_neo4j/neo4j restart


sleep 120


cd ..


now=$(date +"%F %T")
echo "Current time: $now"


cd  GO
echo go

#download go
wget  -O ./go-basic.obo "purl.obolibrary.org/obo/go/go-basic.obo"

python3 ../EFO/transform_obo_to_csv_and_cypher_file.py go-basic.obo GO go $path_to_project > output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate go into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output_cypher_integration.txt 2>&1

sleep 180

$path_neo4j/neo4j restart


sleep 120


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

python3 importAeolus_final.py aeolus_v1/ $path_to_project > output_integration_aeolus.txt 

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate aeolus into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output_cypher_integration.txt 2>&1

sleep 180

$path_neo4j/neo4j restart


sleep 120


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd uniProt
echo UniProt

#python3 parse_uniprot_flat_file_to_tsv.py database/uniprot_sprot.dat $path_to_project > output_integration.txt
python3 parse_uniprot_flat_file_to_tsv.py $path_to_project > output_integration.txt

rm database/*

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate uniprot into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_protein.cypher > output_cypher_integration.txt 2>&1

sleep 180

$path_neo4j/neo4j restart


sleep 120


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

# sleep 180

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

python3 integrate_ncbi_genes_which_are_already_in_hetionet.py $path_to_project > output_generate_integration_file.txt

echo rm gz file
rm data/*

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate ncbi into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_node.cypher > output_cypher_integration.txt 2>&1

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..


now=$(date +"%F %T")
echo "Current time: $now"

cd  IID
echo IID

python3 prepare_human_data_IID.py $path_to_project > output/outputfile.txt

echo rm gz file
rm data/*

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate pathway into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher > output/output_cypher_integration.txt 2>&1

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  pathway
echo pathway

python3 reconstruct_pathway.py $path_to_project > output_generate_integration_file.txt

echo rm gz file
rm data/*

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate pathway into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output_cypher_integration.txt 2>&1

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..


now=$(date +"%F %T")
echo "Current time: $now"


cd  reactome
echo reactome

./script_import_recatome.sh $path_neo4j $path_to_project > output_reactome.txt

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


now=$(date +"%F %T")
echo "Current time: $now"

cd  ClinVar
echo ClinVar

python3 transform_xml_to_nodes_and_edges.py $path_to_project > output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate efo into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_file_node.cypher > output_cypher_node.txt 2>&1

sleep 180

$path_neo4j/neo4j restart


sleep 120

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_file_edges.cypher > output_cypher_edge.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

rm data/*.gz

cd ..

cd  dbSNP
echo dbSNP

#python3 parse_json_to_tsv_dbsnp.py "/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/dbSNP" $path_to_project  > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate efo into neo4j

#$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output/output_cypher_node.txt 2>&1

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..