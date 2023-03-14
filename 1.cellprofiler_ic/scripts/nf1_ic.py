#!/usr/bin/env python
# coding: utf-8

# # Correct illumination and save images for each plate using CellProfiler

# ## Import libraries

# In[1]:


import pathlib

import sys
sys.path.append("../utils")
import cp_utils


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


for plate in plates_info_dictionary:
    # access the plate info stored in the dictionary
    plate_info = plates_info_dictionary[plate]
    path_to_output=plate_info["path_to_output"]
    path_to_images=plate_info["path_to_images"]

    # run illumination correction pipeline and save images
    cp_utils.run_cellprofiler(
        path_to_pipeline=path_to_pipeline,
        path_to_output=path_to_output,
        path_to_images=path_to_images,
        # these variables are turned off for illum pipeline
        sqlite_name=None,
        analysis_run=False,
    )

