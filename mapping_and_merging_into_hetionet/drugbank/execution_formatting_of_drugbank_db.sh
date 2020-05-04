#!/bin/bash
now=$(date +"%F %T")
echo "Current time: $now"

echo rxnorm cui to dugbank id with use of inchikey and unii

echo first rxnorm to unii
python transform_drugbank_to_tsv_final.py > output_transformation.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo second unii to rxnorm
python delete_all_entry_from_drugbank_without_chemical_information_final.py > output_sort_out.txt


now=$(date +"%F %T")
echo "Current time: $now"
