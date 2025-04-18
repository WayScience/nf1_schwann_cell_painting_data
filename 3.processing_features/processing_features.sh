#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash

# activate the preprocessing env
conda activate nf1_preprocessing_env

# convert all notebooks to python files into the scripts folder
jupyter nbconvert --to script --output-dir=scripts/ *.ipynb

# run each python script
python scripts/0.merge_sc_cytotable.py
python scripts/1.sc_cosmicqc.py
python scripts/2.pycytominer_bulk_pipelines.py
python scripts/2.pycytominer_singlecell_pipelines.py
