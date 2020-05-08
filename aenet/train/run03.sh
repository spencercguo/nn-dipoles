#!/bin/bash
#SBATCH -p hns
#SBATCH --job-name=train-x
#SBATCH --nodes=1
#SBATCH --ntasks=20
#SBATCH --time=30:00:00
#SBATCH --mail-type=START,FAIL,END
#SBATCH --mail-user=scguo@stanford.edu

module load ifort
module load imkl
module load impi

train_exe=/home/users/scguo/aenet/bin/train.x-2.0.4-ifort_intelmpi

ln -sf /scratch/users/scguo/aenet-water/dipole/generate-x/water.train
srun -n 20 $train_exe train_bfgs.in > train.out
