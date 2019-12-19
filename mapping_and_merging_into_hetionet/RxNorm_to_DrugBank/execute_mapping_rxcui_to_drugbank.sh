#!/bin/bash
now=$(date +"%F %T")
echo "Current time: $now"

echo rxnorm cui to dugbank id with use of inchikey and unii

echo first rxnorm to unii
python map_rxnorm_to_unii_final.py > output_map_rxnorm_to_unii.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo second unii to rxnorm
python unii_to_rxnorm_cui_final.py > output_unii_to_rxnorm_cui.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo third combine both information and add the unii inchikeys 
python combine_rxnorm_and_fda_srs_to_a_rxnorm_unii_inchkey_file.py > output_combine.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo fourth map rxnorm to drugbank with unii and inchikey

python map_rxcui_to_drugbank_with_unii_inchikey_final.py >  output_map_rxcui_to_drugbank_with_unii_inchikey.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo map drugbank to rxnorm with names

python map_drugbank_to_rxnorm_with_name_final.py >  output_map_drugbank_to_rxnorm_with_name.txt


now=$(date +"%F %T")
echo "Current time: $now"
