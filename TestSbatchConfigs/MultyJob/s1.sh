#!/bin/bash -l

#SBATCH -N 1
#SBATCH -q default
#SBATCH --cpus-per-task=1
#SBATCH --gpus-per-task=-1  # Note: This is invalid, should be 0 or more
#SBATCH --output=logs_Path
#SBATCH --error=error_logs_Path

# Load modules
module load module0
module load module1

# Environment setup from PyEnv
pip install -r requirements.txt
python setup.py install

# Execute command
srun