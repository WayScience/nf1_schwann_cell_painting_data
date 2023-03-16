#!/usr/bin/env python
# coding: utf-8

# # Correct illumination and save images for each plate using CellProfiler

# ## Import libraries

# In[1]:


import pathlib

import sys
sys.path.append("../")
from utils import cp_utils


# ## Set paths for each plate

# In[2]:


path_to_pipeline = pathlib.Path("NF1_illum.cppipe").absolute()

plates_info_dictionary = {
    "Plate_1": {
        "path_to_images": pathlib.Path("../0.download_data/Plate_1/").absolute(),
        "path_to_output": pathlib.Path("Corrected_Plate_1").absolute(),
    },
    "Plate_2": {
        "path_to_images": pathlib.Path("../0.download_data/Plate_2/").absolute(),
        "path_to_output": pathlib.Path("Corrected_Plate_2").absolute(),
    },
}


# ## Run illumination correction pipeline on each plate

# In[3]:


# run through each plate with each set of paths based on dictionary
for plate, info in plates_info_dictionary.items():
    path_to_output = info["path_to_output"]
    path_to_images = info["path_to_images"]
    print(f"Correcting {plate}")

    # run illumination correction pipeline and save images
    cp_utils.run_cellprofiler(
        path_to_pipeline=path_to_pipeline,
        path_to_output=path_to_output,
        path_to_images=path_to_images,
        # these variables are turned off for illum pipeline
        sqlite_name=None,
        analysis_run=False,
    )

