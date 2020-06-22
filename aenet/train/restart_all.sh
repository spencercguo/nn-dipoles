#!/bin/bash

for i in x y z
do
    cd $i/
    rm -f TRAIN*
    rm -f TEST*
    o_ann=$(ls -r O.25t-25t.ann-* | head -n1)
    h_ann=$(ls -r H.25t-25t.ann-* | head -n1)
    cp -f $o_ann O.25t-25t.ann
    cp -f $h_ann H.25t-25t.ann

    echo "#!/bin/bash
#SBATCH -p hns
#SBATCH --job-name=train-$i-restart
#SBATCH --nodes=1
#SBATCH --ntasks=20
#SBATCH --time=12:00:00
#SBATCH --begin=now+6hours
#SBATCH --mail-type=START,FAIL,END
#SBATCH --mail-user=scguo@stanford.edu

module load ifort
module load imkl
module load impi

train_exe=$HOME/aenet/bin/train.x-2.0.4-ifort_intelmpi

srun -n 20 \$train_exe train_bfgs.in > train-restart.out" > restart03.sh

    sbatch restart03.sh
    cd ..
done
