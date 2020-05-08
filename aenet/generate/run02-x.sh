#!/bin/bash
#SBATCH --job-name=generate-x
#SBATCH --nodes=1
#SBATCH --time=02:00:00
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=scguo@stanford.edu

cd $SCRATCH/aenet-water/dipole/generate-x

# setup
ml imkl
ml impi

generate_exe=$HOME/aenet/bin/generate.x-2.0.4-ifort_intelmpi

rm -f water.train*
cp -f temp02.in generate.in
find ../input-x/ -type f 
# number of input structures
wc -l files.txt | awk '{print $1}'>> generate.in
# structure file names
cat files.txt >> generate.in
$generate_exe generate.in > generate.out
