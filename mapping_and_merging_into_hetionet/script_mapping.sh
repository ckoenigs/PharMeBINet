#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

echo $path_to_project

#generate cypher file for adding things to database
echo "" > cypher_general.cypher



cd do
now=$(date +"%F %T")
echo "Current time: $now"
echo 'Integrate Disease Ontology into Hetionet'

python3 fusion_of_disease_ontology_in_hetionet_final_2.py $path_to_project > output_do.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file cypher.cypher > output_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120


cd ..


now=$(date +"%F %T")
echo "Current time: $now"

cd monDO
now=$(date +"%F %T")
echo "Current time: $now"
echo 'change disease identifier to monDO identifier'

./integration_of_mondo.sh $path_neo4j $path_to_project > output_mapping_and_integration.txt 

cd ..

echo Ncbi genes
cd ncbi_gene
now=$(date +"%F %T")
echo "Current time: $now"

python3 integrate_and_update_the_hetionet_gene.py $path_to_project > output_map.txt

echo integrate connection with ne4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file cypher_merge.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120
cd ..

echo GO
cd go
now=$(date +"%F %T")
echo "Current time: $now"

./go_integration.sh $path_neo4j $path_to_project > output_script.txt

cd ..

echo pathway 
cd pathway
now=$(date +"%F %T")
echo "Current time: $now"
echo pathway

python3 switch_identifier_pathway_to_newer_version.py $path_to_project > output_map.txt

echo integrate connection with ne4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/neo4j-shell -file cypher.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120
cd ..


now=$(date +"%F %T")
echo "Current time: $now"

cd uniprot
now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrat uniprot proteins'

./integration_protein.sh $path_neo4j $path_to_project > output_mapping_and_integration.txt 

cd ..


now=$(date +"%F %T")
echo "Current time: $now"
echo drugbank

cd drugbank

./script_mapping_drugbank.sh $path_neo4j/ $path_to_project > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo ctd

cd ctd 

./script_ctd_mapping_and_integration.sh $path_neo4j/ $path_to_project > output_script.txt

cd ..

echo Sider
cd sider
now=$(date +"%F %T")
echo "Current time: $now"
python3 map_Sider_se.py $path_to_project > output_map_se.txt

#python3 map_sider_with_stitch_final.py > output_map_sider.txt

echo integrate sider connection with ne4j shell

#$path_neo4j/neo4j-shell -file map_connection_of_sider_in_hetionet_1.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

cd ..

cd hpo

now=$(date +"%F %T")
echo "Current time: $now"

echo HPO
python3 map_and_integrate_hpo_info_into_hetionet.py > output_hpo_symptomes.txt

$path_neo4j/neo4j-shell -file cypher/connection_symptoms_1.cypher > output_cypher_hpo.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

cd ..

exit 1
cd ..

echo Aeolus outcomes 

now=$(date +"%F %T")
echo "Current time: $now"

cd aeolus/

#python3 map_aeolus_outcome_final.py > output_map_aeolus_outcome.txt


cd ..

cd NDF-RT/
echo ndf-rt

now=$(date +"%F %T")
echo "Current time: $now"
echo disease

#python3 map_NDF-RT_disease_final.py > output_map_ndf_rt_disease.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo drugs

#python3  map_NDF-RT_drug_final.py > output_map_ndf_rt_drugs.txtt


now=$(date +"%F %T")
echo "Current time: $now"
echo integration of ndf-rt connection into hetionet

#$path_neo4j/neo4j-shell -file map_connection_of_ndf_rt_in_hetionet_1.cypher > output_ndf_rt_connection_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

cd ..

cd drugbank
now=$(date +"%F %T")
echo "Current time: $now"
echo 'transformation of drugbank db in tsv and sort drugbank to with chemichal information and not'

#execution_formatting_of_drugbank_db.sh > output_drugbank_shell.txt

cd ..

cd RxNorm_to_DrugBank
now=$(date +"%F %T")
echo "Current time: $now"
echo 'Generate RxNorm CUI-Drugbank ID mapping tables'

#execute_mapping_rxcui_to_drugbank.sh > output_generation_mapping_tables.txt

cd ..


echo Aeolus drugs

now=$(date +"%F %T")
echo "Current time: $now"

cd aeolus/

python3  map_aeolus_drug_new_version.py $path_to_project > output_aeolus_drug.txt


now=$(date +"%F %T")
echo "Current time: $now"

# integration has to be fixed

sleep 180
pathbin/neo4j restart
sleep 120

cd ..


now=$(date +"%F %T")
echo "Current time: $now"

# not ready ...
now=$(date +"%F %T")
echo "Current time: $now"
echo symptoms finding and integration
cd symptoms

now=$(date +"%F %T")
echo "Current time: $now"

echo do
cd Do
python3 use_do_to_find_symptoms_final.py $path_to_project > output_do_symptom.txt

$path_neo4j/neo4j-shell -file cypher/#connection_symptoms_1.cypher > output_cypher_do.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

cd ..


now=$(date +"%F %T")
echo "Current time: $now"
echo umls algorithm

cd umls/
python3 get_symptomes_with_umls_final.py > output_symptomes_umls.txt

cd ..
cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo map symptoms to side effects
cd Map_Symptome_to_SideEffects/
python3 map_symptoms_to_sideEffects_final.py > output_symptoms_to_sideEffects.txt


