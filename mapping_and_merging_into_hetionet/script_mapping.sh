#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

cd drugbank
now=$(date +"%F %T")
echo "Current time: $now"
echo 'transformation of drugbank db in tsv and sort drugbank to with chemichal information and not'

execution_formatting_of_drugbank_db.sh > output_srugbank_shell.txt

cd ..

cd RxNorm_to_DrugBank
now=$(date +"%F %T")
echo "Current time: $now"
echo 'Generate RxNorm CUI-Drugbank ID mapping tables'

execute_mapping_rxcui_to_drugbank.sh > output_generation_mapping_tables.txt

cd ..

cd do
now=$(date +"%F %T")
echo "Current time: $now"
echo 'Integrate Disease Ontology into Hetionet'

python fusion_of_disease_ontology_in_hetionet_final_2.py > output_do.txt

cd ..


echo Sider
cd sider
now=$(date +"%F %T")
echo "Current time: $now"

python map_sider_with_stitch_final.py > output_map_sider.txt

echo integrate sider connection with ne4j shell

$path_neo4j/neo4j-shell -file map_connection_of_sider_in_hetionet_1.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120
cd ..

echo Aeolus outcomes 

now=$(date +"%F %T")
echo "Current time: $now"

cd aeolus/

python map_aeolus_outcome_final.py > output_map_aeolus_outcome.txt

cd ..

cd NDF-RT/
echo ndf-rt

now=$(date +"%F %T")
echo "Current time: $now"
echo disease

python map_NDF-RT_disease_final.py > output_map_ndf_rt_disease.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo drugs

python  map_NDF-RT_drug_final.py > output_map_ndf_rt_drugs.txtt


now=$(date +"%F %T")
echo "Current time: $now"
echo integration of ndf-rt connection into hetionet

$path_neo4j/neo4j-shell -file map_connection_of_ndf_rt_in_hetionet_1.cypher > output_ndf_rt_connection_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

cd ..


cd CTD/
now=$(date +"%F %T")
echo "Current time: $now"
cd ctd
echo phenotype
python map_phenotype_to_hetionet_final.py > output_ctd_phenotype.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo disease to side effects
python map_CTD_disease_to_sideEffects_final.py > output_ctd_disease_to_se.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo disease to disease
python map_CTD_disease_to_Disease_final.py > output_ctd_disease_to_DO.txt

now=$(date +"%F %T")
echo "Current time: $now"


echo chemicals

python map_CTD_drug_to_hetionet_final.py > output_ctd_chemical.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo ctd connection integration


$path_neo4j/neo4j-shell -file map_connection_of_cdt_in_hetionet_1.cypher > output_ctd_connection_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

cd ..


echo Aeolus drugs

now=$(date +"%F %T")
echo "Current time: $now"

cd aeolus/

python  map_aeolus_drugs_final.py > output_aeolus_drug.txt


now=$(date +"%F %T")
echo "Current time: $now"

./script_aeolus_connection_integration_final.sh $path_neo4j

sleep 180
pathbin/neo4j restart
sleep 120

cd ..

# not ready ...
now=$(date +"%F %T")
echo "Current time: $now"
echo symptoms finding and integration
cd symptoms


now=$(date +"%F %T")
echo "Current time: $now"
echo umls algorithm

cd umls/
python importUMLSwithMYSQL_Filter_change_V_NEO4J_3.py > Output/output_13_11.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo map symptoms to side effects
cd Map_Symptome_to_SideEffects/
python map_symptoms_to_sideEffects_2.py > output_symptoms_to_sideEffects.txt

echo end

now=$(date +"%F %T")
echo "Current time: $now"
