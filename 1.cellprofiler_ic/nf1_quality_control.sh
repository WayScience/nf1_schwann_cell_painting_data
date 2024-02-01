#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the main conda environment
conda activate nf1_cellpainting_data

# convert all notebooks to python files into the scripts folder in the image_quality_control folder
jupyter nbconvert --to python --output-dir=image_quality_control/scripts/ image_quality_control/*.ipynb

# run the image quality control scripts
python image_quality_control/scripts/0.whole_image_qc.py
python image_quality_control/scripts/1.evaluate_qc.py
Rscript image_quality_control/scripts/2.qc_report.r
