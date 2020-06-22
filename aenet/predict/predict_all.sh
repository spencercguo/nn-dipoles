#!/bin/bash

for i in x y z
do
    mkdir $i
    cp -f temp04.in $i
    cd $i
    echo "#!/bin/bash
#SBATCH --job-name=predict-$i
#SBATCH --nodes=1
#SBATCH --ntasks=20
#SBATCH --time=12:00:00
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=scguo@stanford.edu

# setup
ml python/3.6.1
ml py-numpy/1.17.2_py36
ml ifort
ml imkl
ml impi

predict_exe=$HOME/aenet/bin/predict.x-2.0.4-ifort_intelmpi

min_ann=\$(python3 ../find_min.py ../../train/$i/train.out)

ln -sf \$min_ann .
ln -sf \${min_ann%/*}/train.out

min_ann_O=\$(ls O.*.ann-*)
min_ann_H=\$(ls H.*.ann-*)

cp -f temp04.in predict.in
sed -i -e \"~s|XXXNN01|\$min_ann_O|\" predict.in
sed -i -e \"~s|XXXNN02|\$min_ann_H|\" predict.in
find ../../generate-$i -type f > files.txt
wc -l files.txt | awk '{print \$1}' >> predict.in
cat files.txt >> predict.in

srun -n 20 \$predict_exe predict.in > predict.out

python3 ../compute_force_error.py > errors.out" > run04.sh
    sbatch run04.sh
    cd ../
done
