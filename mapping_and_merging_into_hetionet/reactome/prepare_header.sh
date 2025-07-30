#!/bin/bash

echo $1
#
head -1 $1 > IUPHAR/version.txt

tail -n+2 $1 > test.tsv

cp test.tsv $1

rm test.tsv


