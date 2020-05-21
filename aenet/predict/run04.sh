#!/bin/bash
#SBATCH --job-name=predict
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=06:00:00
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=scguo@stanford.edu

# cd $SCRATCH/aenet-water/04_predict/

# setup
ml python/3.6.1
ml py-numpy/1.17.2_py36
ml ifort
ml imkl
ml impi

predict_exe=$HOME/aenet/bin/predict.x-2.0.4-ifort_intelmpi

min_ann=$(python3 find_min.py ../train/x/train.out)

ln -sf $min_ann .
ln -sf ${min_ann%/*}/train.out

min_ann_O=$(ls O.*.ann-*)
min_ann_H=$(ls H.*.ann-*)

cp -f temp04.in predict.in
sed -i -e "~s|XXXNN01|$min_ann_O|" predict.in
sed -i -e "~s|XXXNN02|$min_ann_H|" predict.in
wc -l ../generate-x/files.txt | awk '{print $1}'>> predict.in
cat ../generate-x/files.txt >> predict.in

srun -n 16 $predict_exe predict.in > predict.out

python3 compute_force_error.py > errors.out
