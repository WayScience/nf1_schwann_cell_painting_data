#!/usr/bin/env python
# coding: utf-8

# # Perform segmentation and feature extraction for each plate using CellProfiler

# ## Import libraries

# In[1]:


import pathlib

import sys
sys.path.append("../")
from utils import cp_utils


# ## Set paths for each plate

# In[2]:


path_to_output = pathlib.Path("./analysis_output").resolve(strict=True)

plates_info_dictionary = {
    "Plate_1": {
        "path_to_pipeline" : pathlib.Path("NF1_analysis_plate1_plate2.cppipe").resolve(strict=True),
        "path_to_images": pathlib.Path("../1.cellprofiler_ic/Corrected_Plate_1/").resolve(strict=True),
    },
    "Plate_2": {
        "path_to_pipeline" : pathlib.Path("NF1_analysis_plate1_plate2.cppipe").resolve(strict=True),
        "path_to_images": pathlib.Path("../1.cellprofiler_ic/Corrected_Plate_2/").resolve(strict=True), 
    },
    "Plate_3": {
        "path_to_pipeline" : pathlib.Path("NF1_analysis_plate3_plate3'.cppipe").resolve(strict=True),
        "path_to_images": pathlib.Path("../1.cellprofiler_ic/Corrected_Plate_3/").resolve(strict=True), 
    },
}


# ## Run illumination correction pipeline on each plate
# 
# This cell is not finished to completion due to how long it would take. It is ran in the python file instead.

# In[3]:


# run through each plate with each set of paths based on dictionary
for plate, info in plates_info_dictionary.items():
    path_to_pipeline = info["path_to_pipeline"]
    path_to_images = info["path_to_images"]
    print(f"Running analysis on {plate}!")

    # run analysis pipeline
    cp_utils.run_cellprofiler(
        path_to_pipeline=path_to_pipeline,
        path_to_output=path_to_output,
        path_to_images=path_to_images,
        # name each SQLite file after plate name
        sqlite_name=plate,
        analysis_run=True,
    )

