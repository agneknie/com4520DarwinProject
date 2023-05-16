#!/bin/bash
# 16GB of RAM
#SBATCH --mem=16G
# email 
#SBATCH --mail-user=@sheffield.ac.uk
#SBATCH --mail-type=BEGIN,END,FAIL
# set job name
#SBATCH --job-name=generate_glosses
# set output path to R-[job_name].[job_id].out
#SBATCH --output=R-%x.%j.out
# get gpu
#SBATCH --partition=gpu
#SBATCH --qos=gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1

module load Anaconda3/5.3.0
module load cuDNN/7.6.4.38-gcccuda-2019b

conda create -n pytorch python=3.8

source activate pytorch

pip install torch torchvision

dir=$(pwd)

git clone https://oauth2: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@github.com/agneknie/com4520DarwinProject.git
cd com4520DarwinProject
git checkout framework-gloss
pip install -r requirements.txt

python hpc/generate_glosses.py  --n-glosses=1 --input-file=$dir/bronze.csv --output-file=$dir/gloss_train_1.csv
python hpc/generate_glosses.py  --n-glosses=2 --input-file=$dir/bronze.csv --output-file=$dir/gloss_train_2.csv
python hpc/generate_glosses.py  --n-glosses=3 --input-file=$dir/bronze.csv --output-file=$dir/gloss_train_3.csv
