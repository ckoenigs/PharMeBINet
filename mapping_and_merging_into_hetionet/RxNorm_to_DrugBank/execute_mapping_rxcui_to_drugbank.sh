#!/bin/bash

counter_of_connection_tries=0
worked_url=false
now=$(date +"%F %T")
echo "Current time: $now"
echo down load fda file

python3 download_unii_data.py


unzip UNII_Data*.zip -d unii/
cd unii
# unzip UNII_Data.zip -d .
mv UNII_Records* unii_data.txt
cd ..


now=$(date +"%F %T")
echo "Current time: $now"
echo load drugbank information 
python3 generate_unii_drugbank_table_with_drugbank.py > output/output_drugbank_info.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo rxnorm cui to dugbank id with use of inchikey and unii

echo first rxnorm to unii
python3 map_rxnorm_to_unii_final.py > output/output_map_rxnorm_to_unii.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo second unii to rxnorm
python3 unii_to_rxnorm_cui_final.py > output/output_unii_to_rxnorm_cui.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo third combine both information and add the unii inchikeys 
python3 combine_rxnorm_and_fda_srs_to_a_rxnorm_unii_inchkey_file.py > output/output_combine.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo fourth map rxnorm to drugbank with unii and inchikey

python3 map_rxcui_to_drugbank_with_unii_inchikey_final.py >  output/output_map_rxcui_to_drugbank_with_unii_inchikey.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo map drugbank to rxnorm with names
#take a lot of time
python3 map_drugbank_to_rxnorm_with_name_final.py >  output/output_map_drugbank_to_rxnorm_with_name.txt


now=$(date +"%F %T")
echo "Current time: $now"

rm unii/*
rm UNII_Data*.zip
