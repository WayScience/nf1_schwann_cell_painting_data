#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash

# activate the main conda environment
conda activate nf1_cellpainting_data

# convert all notebooks to python files into the scripts folder
jupyter nbconvert --to python --output-dir=scripts/ *.ipynb

# run jupyter notebooks
jupyter nbconvert --to=html \
    --FilesWriter.build_directory=scripts/html \
    --ExecutePreprocessor.kernel_name=python3 \
    --ExecutePreprocessor.timeout=10000000 \
    --execute 0.merge_sc_cytotable

jupyter nbconvert --to=html \
    --FilesWriter.build_directory=scripts/html \
    --ExecutePreprocessor.kernel_name=python3 \
    --ExecutePreprocessor.timeout=10000000 \
    --execute 1.pycytominer_bulk_pipelines.ipynb

jupyter nbconvert --to=html \
    --FilesWriter.build_directory=scripts/html \
    --ExecutePreprocessor.kernel_name=python3 \
    --ExecutePreprocessor.timeout=10000000 \
    --execute 2.pycytominer_singlecell_pipelines.ipynb
