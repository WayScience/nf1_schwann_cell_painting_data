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
# 
# Note: Output file path does not need to be strict since the `run_cellprofiler` function can create the output folder directory if it doesn't already exist. The other paths must be strict since these files should already exist for CellProfiler to run. The output directory doesn't need to already exist.

# In[2]:


plates_info_dictionary = {
    "Plate_1": {
        "path_to_pipeline": pathlib.Path("NF1_illum_Plates_1_2.cppipe").resolve(strict=True),
        "path_to_images": pathlib.Path("../0.download_data/Plate_1/").resolve(strict=True),
        "path_to_output": pathlib.Path("Corrected_Plate_1").resolve(),
    },
    "Plate_2": {
        "path_to_pipeline": pathlib.Path("NF1_illum_Plates_1_2.cppipe").resolve(strict=True),
        "path_to_images": pathlib.Path("../0.download_data/Plate_2/").resolve(strict=True),
        "path_to_output": pathlib.Path("Corrected_Plate_2").resolve(),
    },
    "Plate_3": {
        "path_to_pipeline": pathlib.Path("NF1_illum_Plate3_Plate3prime.cppipe").resolve(strict=True),
        "path_to_images": pathlib.Path("../0.download_data/Plate_3/").resolve(strict=True),
        "path_to_output": pathlib.Path("Corrected_Plate_3").resolve(),
    },
    "Plate_3_prime": {
        "path_to_pipeline": pathlib.Path("NF1_illum_Plate3_Plate3prime.cppipe").resolve(strict=True),
        "path_to_images": pathlib.Path("../0.download_data/Plate_3_prime/").resolve(strict=True),
        "path_to_output": pathlib.Path("Corrected_Plate_3_prime").resolve(),
    }
}


# ## Run illumination correction pipeline on each plate
# 
# In this notebook, we do not run the cells to completion as we prefer to run the notebooks as nbconverted python files due to better stability.

# In[3]:


# run through each plate with each set of paths based on dictionary
for plate, info in plates_info_dictionary.items():
    path_to_pipeline = info["path_to_pipeline"]
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

