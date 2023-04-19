#!/bin/bash

# this line is needed for the sh file to properly activate a conda environment 
eval "$(conda shell.bash hook)"
# activate the main conda environment (if not already activated)
conda activate nf1_cellpainting_data

# convert the notebook into a python and run the notebook
jupyter nbconvert --to python \
        --FilesWriter.build_directory=scripts/ \
        --execute download_plates.ipynb
