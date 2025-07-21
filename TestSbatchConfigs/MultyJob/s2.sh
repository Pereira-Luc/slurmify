#!/bin/bash -l

#SBATCH -N 2
#SBATCH -q default
#SBATCH --cpus-per-task=0  # Note: This is unusual, should be at least 1
#SBATCH --gpus-per-task=1
#SBATCH --output=logs_Path
#SBATCH --error=error_logs_Path

# Load modules
module load module0
module load module1

# Environment setup from PyEnv
pip install -r requirements.txt
python setup.py install

# Environment setup from Exports
export PATH=/some/path:$PATH
export VAR=value

# Execute command
srun