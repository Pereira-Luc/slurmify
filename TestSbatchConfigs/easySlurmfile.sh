#!/bin/bash -l

#SBATCH -A lxp
#SBATCH -q default
#SBATCH -N 2
#SBATCH --cpus-per-task=1
#SBATCH --gpus-per-task=1
#SBATCH --output=logs_Path
#SBATCH --error=error_logs_Path

# Load modules
module load module0
module load module1

# Environment setup
pip install -r requirements.txt
python setup.py install

# Execute command
srun ...