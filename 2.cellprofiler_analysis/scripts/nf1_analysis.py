#!/usr/bin/env python
# coding: utf-8

# # Perform segmentation and feature extraction for each plate using CellProfiler

# ## Import libraries

# In[1]:


import sys
import pathlib

sys.path.append("../")
from utils import cp_utils

# ## Set paths for each plate
# 
# Note: Due to the difference channel numbers between plates 1 + 2 (3 channels) and plates 3 + 3 prime (4 channels), there needs to be two difference cppipe files (like in the IC module). 
# 
# As well, the output file path does not need to be strict since the `run_cellprofiler` function can create the output folder directory if it doesn't already exist. The other paths must be strict since these files should already exist for CellProfiler to run. The output directory doesn't need to already exist.

# In[2]:


path_to_output = pathlib.Path("./analysis_output").resolve()

plates_info_dictionary = {
    "Plate_1": {
        # this pipeline is specific to plates 1 and 2
        "path_to_pipeline": pathlib.Path("NF1_analysis_plate1_plate2.cppipe").resolve(
            strict=True
        ),
        "path_to_images": pathlib.Path(
            "../1.cellprofiler_ic/Corrected_Plate_1/"
        ).resolve(strict=True),
    },
    "Plate_2": {
        # this pipeline is specific to plates 1 and 2
        "path_to_pipeline": pathlib.Path("NF1_analysis_plate1_plate2.cppipe").resolve(
            strict=True
        ),
        "path_to_images": pathlib.Path(
            "../1.cellprofiler_ic/Corrected_Plate_2/"
        ).resolve(strict=True),
    },
    "Plate_3": {
        # this pipeline is specific to plates 3 and 3'
        "path_to_pipeline": pathlib.Path("NF1_analysis_plate3_plate3prime.cppipe").resolve(
            strict=True
        ),
        "path_to_images": pathlib.Path(
            "../1.cellprofiler_ic/Corrected_Plate_3/"
        ).resolve(strict=True),
    },
    "Plate_3_prime": {
        # this pipeline is specific to plates 3 and 3'
        "path_to_pipeline": pathlib.Path("NF1_analysis_plate3_plate3prime.cppipe").resolve(
            strict=True
        ),
        "path_to_images": pathlib.Path(
            "../1.cellprofiler_ic/Corrected_Plate_3_prime/"
        ).resolve(strict=True),
    },
}

# ## Run analysis pipeline on each plate
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
