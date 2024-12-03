#!/bin/bash
#SBATCH --job-name=super-yolo-job5
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

python train.py --cfg models/SRyolo_MF.yaml --train_img_size 512 --data  data/server-SRvedai.yaml --ch 64 --epochs 300 --batch-size 4 --input_mode RGB+IR+MF