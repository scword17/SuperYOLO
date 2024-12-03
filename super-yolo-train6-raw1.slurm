#!/bin/bash
#SBATCH --job-name=super-yolo-job3
#SBATCH --partition=cngpu
#SBATCH --mem=16G
#SBATCH --nodes=1
#SBATCH -o Test%j.out
#SBATCH -e Test%j.err
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=3
srun env | grep CUDA


module load compilers/nvidia/cuda-11.3
module load anaconda3/4.10.1
conda activate yolo-yk-new

python train.py --cfg models/SRyolo_noFocus_small.yaml --train_img_size 512 --data data/server-SRvedai.yaml --ch 3 --batch-size 16 --input_mode RGB