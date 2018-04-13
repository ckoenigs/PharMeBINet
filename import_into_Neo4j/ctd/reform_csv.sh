#!/bin/bash

find ./ctd_data/ -name *.csv | while read fname
do
    echo $fname
    tail -n+28 $fname | sed 0,/#\ /s/#\ // | sed '2d' > test.txt
    cp test.txt $fname
done

rm test.txt
