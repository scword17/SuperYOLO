#!/bin/bash
#SBATCH --job-name=super-yolo-job4
#SBATCH --partition=cnGPUtest
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

python train.py --cfg models/SRyolo_noFocus_small.yaml --super --train_img_size 1024 --hr_input --data data/server-SRvedai.yaml --ch 3  --epochs 300 --batch-size 2 --input_mode RGB