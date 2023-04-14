#!/bin/bash

# this line is needed for the sh file to properly activate a conda environment 
eval "$(conda shell.bash hook)"
# activate the main conda environment
conda activate nf1_test_env

# convert the notebook into a python and run the file
jupyter nbconvert --to python \
        --FilesWriter.build_directory=scripts/ \
        --execute nf1_analysis.ipynb
