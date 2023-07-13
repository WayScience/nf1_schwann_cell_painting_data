#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the main conda environment
conda activate nf1_cellpainting_data

# convert the notebook into a python and run the notebook
jupyter nbconvert --to python \
        --FilesWriter.build_directory=scripts/ \
        --execute download_plates.ipynb
