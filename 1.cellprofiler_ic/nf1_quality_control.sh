#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the main conda environment
conda activate nf1_cellpainting_data

# go into the image_quality_control directory
cd image_quality_control

# convert all notebooks to python files into the scripts folder in the image_quality_control folder
jupyter nbconvert --to script --output-dir=scripts/ image_quality_control/*.ipynb

# run the image quality control scripts (python)
python image_quality_control/scripts/0.whole_image_qc.py # Comment out unless you have made changes to the QC pipeline
python scripts/1.evaluate_qc.py

# deactivate the main conda environment
conda deactivate

# activate the R specific conda environment (from 4.analyze_data)
conda activate r_analysis_nf1

# run the image quality control R script
Rscript scripts/2.qc_report.r

# return back to original directory
cd ...
