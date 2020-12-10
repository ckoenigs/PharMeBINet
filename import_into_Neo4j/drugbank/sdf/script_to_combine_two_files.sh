#!/bin/bash

if (($# != 3)); then
    echo 'need two arguments to combine and the last one which should be the combined file'
    exit 
fi

# remove the first line header
tail -n +2 $2 > bluby.csv

now=$(date +"%F %T")
echo "Current time: $now"
cat $1 bluby.csv > $3

rm bluby.csv
