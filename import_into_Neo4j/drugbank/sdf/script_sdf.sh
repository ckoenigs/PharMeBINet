#!/bin/bash

path_to_drugbank_data=$1

now=$(date +"%F %T")
echo "Current time: $now"
echo metabolite

python3 new_sdf_parser.py $path_to_drugbank_data/structure/metabolite-structures.sdf metabolite_structure.tsv


now=$(date +"%F %T")
echo "Current time: $now"
echo structure

python3 new_sdf_parser.py $path_to_drugbank_data/structure/structures.sdf structure.tsv