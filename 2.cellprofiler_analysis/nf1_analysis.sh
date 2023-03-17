#!/bin/bash

# activate the main conda environment
eval "$(conda shell.bash hook)"
conda activate nf1_cellpainting_data

# convert the notebook into a python and run the file
jupyter nbconvert --to python \
        --FilesWriter.build_directory=scripts/ \
        --execute nf1_analysis.ipynb
