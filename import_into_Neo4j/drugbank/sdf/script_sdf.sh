#!/bin/bash

now=$(date +"%F %T")
echo "Current time: $now"
echo metabolite

python3 new_sdf_parser.py metabolite-structures.sdf metabolite_structure.csv


now=$(date +"%F %T")
echo "Current time: $now"
echo structure

python3 new_sdf_parser.py structures.sdf structure.csv