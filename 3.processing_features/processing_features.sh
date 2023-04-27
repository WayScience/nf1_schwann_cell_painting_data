#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the main conda environment
conda activate nf1_cellpainting_data

# convert all notebooks to python files into the scripts folder
jupyter nbconvert --to python --output-dir=scripts/ *.ipynb

# run the python scripts in order (from convert+merge, annotate, normalize, and feature select)
python scripts/merge_sc_cytotable.py && python scripts/annotate_sc.py && python scripts/normalize_sc.py && python scripts/feature_select_sc.py
