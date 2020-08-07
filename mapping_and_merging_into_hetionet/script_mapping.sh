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

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output_cypher.txt

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


now=$(date +"%F %T")
echo "Current time: $now"

cd ..

echo Ncbi genes
cd ncbi_gene
now=$(date +"%F %T")
echo "Current time: $now"

python3 integrate_and_update_the_hetionet_gene.py $path_to_project > output_map.txt

echo integrate connection with ne4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120
cd ..



echo OMIM
cd omim

now=$(date +"%F %T")
echo "Current time: $now"
echo gene and disease

python3 integrate_omim_genes_phenotypes.py $path_to_project > output/output_map_gene_phenotype.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 integrate_omim_predominantly_phenotypes.py $path_to_project > output/output_map_phenotype.txt

echo integrate connection with ne4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_gene_phenotype.cypher > output/output_cypher_integration_gene_disease.txt

sleep 180

$path_neo4j/neo4j restart

sleep 120

echo integrate connection with ne4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_phenotype.cypher > output/output_cypher_integration_disease.txt

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

cd pathway
now=$(date +"%F %T")
echo "Current time: $now"
echo pathway

python3 switch_identifier_pathway_to_newer_version.py $path_to_project > output_map.txt

echo integrate connection with ne4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120
cd ..



echo Clinvar 
cd clinvar
now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_clinvar_variation.py $path_to_project > output_map_variant.txt

echo integrate connection with ne4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_variants.cypher > output/output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_disease_clinvar.py $path_to_project > output_map.txt

echo integrate connection with ne4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f disease/cypher_disease.cypher > output_cypher_integration.txt

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
echo mapping table rxcui drugbank

cd RxNorm_to_DrugBank 

./execute_mapping_rxcui_to_drugbank.sh > output.txt

cd ..


cd hpo

now=$(date +"%F %T")
echo "Current time: $now"

echo HPO
python3 map_and_integrate_hpo_info_into_hetionet.py $path_to_project > output/output_hpo_disease.txt

$path_neo4j/cypher-shell -u neo4j -p test -f cypher/cypher_disease.cypher > cypher/output_cypher_hpo.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

python3 map_hpo_symptoms_into_hetionet.py $path_to_project > output/output_hpo_symptomes.txt

$path_neo4j/cypher-shell -u neo4j -p test -f cypher/cypher_symptom.cypher > cypher/output_cypher_hpo_symptom.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

python3 integrat_hpo_disease_symptom_rela.py $path_to_project > output/output_hpo_symptomes.txt

$path_neo4j/cypher-shell -u neo4j -p test -f cypher/cypher_edge.cypher > cypher/output_cypher_hpo_edge.txt 2>&1

sleep 180
$path_neo4j/neo4j restart
sleep 120



cd ..




now=$(date +"%F %T")
echo "Current time: $now"
echo ctd

cd ctd 

./script_ctd_mapping_and_integration.sh $path_neo4j/ $path_to_project > output_script.txt

cd ..



now=$(date +"%F %T")
echo "Current time: $now"
echo drugbank Protein

cd drugbank

./script_map_drugbank_protein.sh $path_neo4j/ $path_to_project > output_script.txt

cd ..

echo Sider
cd sider
now=$(date +"%F %T")
echo "Current time: $now"
echo se
python3 map_Sider_se.py $path_to_project > output_map_se.txt

echo integrate se with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_se.cypher > output_cypher_integration_se.txt

sleep 180

$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo drug
python3 map_sider_drug.py $path_to_project > output_map_drug.txt

echo integrate se with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_drug.cypher > output_cypher_integration_drug.txt

sleep 180

$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo drug
python3 integrate_rela_drug_side_effect.py $path_to_project > output_map_rela.txt

echo integrate relationships
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_rela.cypher > output_cypher_integration_drug.txt

sleep 180

$path_neo4j/neo4j restart
sleep 120



cd ..
echo Aeolus outcomes 

now=$(date +"%F %T")
echo "Current time: $now"

cd aeolus

python3 map_aeolus_outcome_final.py $path_to_project > output_map_aeolus_outcome.txt


echo integrate se with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_se.cypher > output_cypher_integration_se.txt

sleep 180

$path_neo4j/neo4j restart
sleep 120


echo Aeolus drugs

now=$(date +"%F %T")
echo "Current time: $now"


python3  map_aeolus_drugs_final.py $path_to_project > output_aeolus_drug.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output_cypher_integration_drug.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

echo relationships
python3  integrate_aeolus_relationships.py $path_to_project > output_aeolus_drug.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_rela.cypher > output_cypher_integration_rela.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

cd ..


cd ndf-rt/
echo ndf-rt

now=$(date +"%F %T")
echo "Current time: $now"
echo disease

python3 map_NDF-RT_disease_final.py $path_to_project > output_map_ndf_rt_disease.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f disease/cypher.cypher > disease/output_cypher_integration_se.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120



now=$(date +"%F %T")
echo "Current time: $now"
echo drugs

python3  map_NDF_RT_drug.py $path_to_project > output_map_ndf_rt_drugs.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integration of ndf-rt connection into hetionet

$path_neo4j/cypher-shell -u neo4j -p test -f drug/cypher.cypher > output_ndf_rt_drug_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120



now=$(date +"%F %T")
echo "Current time: $now"
echo drugs

python3  integrate_ndf_rt_drug_disease_rela.py $path_to_project > output_map_ndf_rt_rela.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integration of ndf-rt connection into hetionet

$path_neo4j/cypher-shell -u neo4j -p test -f relationships/cypher.cypher > output_ndf_rt_rela_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120

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


