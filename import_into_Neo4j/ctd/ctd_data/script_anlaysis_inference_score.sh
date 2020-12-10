#!/bin/bash
number=$3
how_much_down=$4
echo "Bash version ${BASH_VERSION}..."
for i in {1..12..1}
do
    python find_all_scores_of_disease_gene.py $1 $2 $number
    number=$(($number-10))
done
