#!/bin/bash

for i in *.txt; do
    echo $i
    ./prepare_header.sh $i
done
