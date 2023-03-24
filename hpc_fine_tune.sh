#!/bin/bash
# 16GB of RAM
#SBATCH --mem=16G
# email 
#SBATCH --mail-user=aallsebrook1@sheffield.ac.uk
#SBATCH --mail-type=BEGIN,END,FAIL
# set job name
#SBATCH --job-name=fine_tune_bronze
#SBATCH --output=R-%x.%j.out
# get gpus
#SBATCH --partition=gpu
#SBATCH --qos=gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1

module load Anaconda3/5.3.0
module load cuDNN/7.6.4.38-gcccuda-2019b

conda create -n pytorch python=3.6

source activate pytorch

pip install torch torchvision

dir=$(pwd)

git clone https://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@github.com/agneknie/com4520DarwinProject.git
cd com4520DarwinProject
git checkout framework-hpc
pip install -r requirements.txt
conda-develop $dir/com4520DarwinProject/src

python fine_tune_model.py --en --num-epochs=1 --batch-size=32 --seed=4 --tokenize-idioms --base-model="$dir/base_model_tokenized" --train-file="$dir/bronze.csv" --dev-path="$dir/com4520DarwinProject/data/datasets/SemEval_2022_Task2_SubTaskB/EvaluationData" --output-path="$dir/model_bronze"

