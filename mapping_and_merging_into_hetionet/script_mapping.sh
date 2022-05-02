#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

echo $path_to_project

#generate cypher file for adding things to database
echo "" > cypher_general.cypher






cd monDO
now=$(date +"%F %T")
echo "Current time: $now"
echo 'change disease identifier to monDO identifier'

./integration_of_mondo.sh $path_neo4j $path_to_project > output_mapping_and_integration.txt


cd ..


now=$(date +"%F %T")
echo "Current time: $now"
echo extract disease info before do

# $path_neo4j/cypher-shell -u neo4j -p test -f cypher_export_disease_before_do.cypher 


cd do
now=$(date +"%F %T")
echo "Current time: $now"
echo do

./script_do.sh $path_neo4j $path_to_project > output_script.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo extract disease info after do

# $path_neo4j/cypher-shell -u neo4j -p test -f cypher_export_disease_after_do.cypher 


cd ncbi_gene
now=$(date +"%F %T")
echo "Current time: $now"
echo Ncbi genes

./script_ncbi.sh $path_neo4j $path_to_project > output_script.txt


sleep 120
cd ..



cd omim

now=$(date +"%F %T")
echo "Current time: $now"
echo OMIM

./script_omim.sh $path_neo4j $path_to_project > output_script.txt



cd ..

cd pathway
now=$(date +"%F %T")
echo "Current time: $now"
echo pathway

./script_pathway.sh $path_neo4j $path_to_project > output_script.txt

cd ..


cd uniprot
now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrat uniprot proteins'

./integration_protein.sh $path_neo4j $path_to_project > output_mapping_and_integration.txt 

cd ..

cd go
now=$(date +"%F %T")
echo "Current time: $now"
echo GO

./go_integration.sh $path_neo4j $path_to_project > output_script.txt


cd ..


cd iid
now=$(date +"%F %T")
echo "Current time: $now"
echo 'IID'

./script_iid.sh $path_neo4j $path_to_project > output_script.txt

cd ..

cd reactome
now=$(date +"%F %T")
echo "Current time: $now"
echo reactome

./script_reactome.sh $path_neo4j $path_to_project > output_script.txt

cd ..

cd hmdb
now=$(date +"%F %T")
echo "Current time: $now"
echo hmdb protein, go, metabolite

# ./script_hmdb_mapping_and_merging.sh $path_neo4j $path_to_project > output_script_part_1.txt

cd ..

cd smpdb
now=$(date +"%F %T")
echo "Current time: $now"
echo smpdb

# ./script_to_mapping_smpdb.sh $path_neo4j $path_to_project > output_script.txt

cd ..


now=$(date +"%F %T")
echo "Current time: $now"
echo Clinvar 
cd clinvar

./script_clinvar.sh $path_neo4j $path_to_project > output_mapping_and_integration.txt 

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo drugbank

cd drugbank

./script_mapping_drugbank.sh $path_neo4j/ $path_to_project > output_script.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo mapping table rxcui drugbank

cd RxNorm_to_DrugBank 

./execute_mapping_rxcui_to_drugbank.sh > output.txt

cd ..


cd hpo

now=$(date +"%F %T")
echo "Current time: $now"

echo HPO

./script_hpo.sh $path_neo4j/ $path_to_project > output_script.txt


cd ..

cd hmdb
now=$(date +"%F %T")
echo "Current time: $now"
echo hmdb pathway, disease

# ./script_hmdb_mapping_and_merging_part2.sh $path_neo4j $path_to_project > output_script_part_2.txt

cd ..


now=$(date +"%F %T")
echo "Current time: $now"
echo ctd

cd ctd 

./script_ctd_mapping_and_integration.sh $path_neo4j/ $path_to_project > output_script.txt

cd ..

sleep 120 
$path_neo4j/neo4j restart
sleep 120


cd ndf-rt/
now=$(date +"%F %T")
echo "Current time: $now"
echo ndf-rt


./script_ndf_rt.sh $path_neo4j/ $path_to_project > output_script.txt


cd ..


cd DDinter
now=$(date +"%F %T")
echo "Current time: $now"
echo DDinter

# ./script_execute_DDinter.sh $path_neo4j $path_to_project > output_script.txt

cd ..

cd reactome
now=$(date +"%F %T")
echo "Current time: $now"
echo reactome drug

./script_reactome_drug.sh $path_neo4j $path_to_project > output_script_drug.txt

cd ..


cd clinvar

now=$(date +"%F %T")
echo "Current time: $now"
echo clinvar drug response

./script_clinvar_drug_response.sh $path_neo4j/ $path_to_project > output_script.txt

cd ..



now=$(date +"%F %T")
echo "Current time: $now"
echo drugbank Protein

cd drugbank

./script_map_drugbank_protein.sh $path_neo4j/ $path_to_project > output_script_protein.txt

cd ..

cd atc
now=$(date +"%F %T")
echo "Current time: $now"
echo 'atc'

./script_atc.sh $path_neo4j/ $path_to_project > output_script.txt

cd ..

cd sider
now=$(date +"%F %T")
echo "Current time: $now"
echo Sider

./script_sider.sh $path_neo4j/ $path_to_project > output_script.txt

cd ..

cd disgenet
now=$(date +"%F %T")
echo "Current time: $now"
echo DisGeNet

# ./script_to_integrate_disgenet.sh $path_neo4j $path_to_project > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo Aeolus  

cd aeolus

./script_aeolus.sh $path_neo4j/ $path_to_project > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo ADReCS-Target  

cd adrecs_target

# ./script_to_integrate_ADReCS_Target.sh $path_neo4j $path_to_project > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo PharmGKB
cd pharmGKB

./script_pharmgkb.sh $path_neo4j/ $path_to_project > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo DrugCentral
cd drugcentral

# ./script_to_map_and_integrate_drug_central_information.sh $path_neo4j $path_to_project > output_script.txt

cd ..


now=$(date +"%F %T")
echo "Current time: $now"
echo map symptoms to side effects
cd connectSideEffect_Sympom_Disease/

./script_phenotyp_mapping.sh $path_neo4j/ $path_to_project > output_script.txt


cd ..



now=$(date +"%F %T")
echo "Current time: $now"
echo dbSNP
cd dbSNP

./script_to_get_dbSNPs_information.sh $path_neo4j $path_to_project > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo PharmGKB edges
cd pharmGKB

./script_pharmgkb_edges.sh $path_neo4j/ $path_to_project > output_script_edges.txt

cd ..


exit 1


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

$path_neo4j/cypher-shell -u neo4j -p test -f cypher/#connection_symptoms_1.cypher > output_cypher_do.txt

sleep 120
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


