#!/bin/bash

cd input-z
for n in {0..99}
do
    for m in {0..127}
    do
        head "input_${n}_${m}.xsf" -n1 | awk 'NF>1{print $NF}' >> "../test-z.out"
    done
done
cd .. 
