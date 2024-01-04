#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash

# activate the main conda environment
conda activate nf1_cellpainting_data

# convert all notebooks to python files into the scripts folder
jupyter nbconvert --to python --output-dir=scripts/ *.ipynb

# run each python script
python scripts/0.merge_sc_cytotable.py
python scripts/1.pycytominer_bulk_pipelines.py
python scripts/2.pycytominer_singlecell_pipelines.py
