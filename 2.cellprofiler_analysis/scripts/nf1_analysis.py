#!/usr/bin/env python
# coding: utf-8

# # Perform segmentation and feature extraction for each plate using CellProfiler Parallel

# ## Import libraries

# In[1]:


import pathlib
import pprint

import sys

sys.path.append("../utils")
import cp_parallel


# ## Set paths and variables

# In[2]:


# set the run type for the parallelization
run_name = "analysis"

# set main output dir for all plates
output_dir = pathlib.Path("./analysis_output")
output_dir.mkdir(exist_ok=True)

# directory where images are located within folders
images_dir = pathlib.Path("../1.cellprofiler_ic/Corrected_Images/")

# list for plate names based on folders to use to create dictionary
plate_names = []
# iterate through 0.download_data and append plate names from folder names that contain image data from that plate
for file_path in pathlib.Path("../0.download_data/").iterdir():
    if str(file_path.stem).startswith("Plate"):
        plate_names.append(str(file_path.stem))

print(plate_names)


# ## Create dictionary with all info for each plate

# In[3]:


# create plate info dictionary with all parts of the CellProfiler CLI command to run in parallel
plate_info_dictionary = {
    name: {
        "path_to_images": pathlib.Path(
            list(images_dir.rglob(f"Corrected_{name}"))[0]
        ).resolve(strict=True),
        "path_to_output": pathlib.Path(f"{output_dir}/{name}"),
    }
    for name in plate_names if name=="Plate_5" # focus on plate 5
}

# iterate over the dictionary and add the path_to_pipeline specific for each plate
for name, info in plate_info_dictionary.items():
    # only plates 1 and 2 have 3 channels so these are the only plates that use this path
    if name == "Plate_1" or name == "Plate_2":
        info["path_to_pipeline"] = pathlib.Path(
            f"./NF1_analysis_3channel.cppipe"
        ).resolve(strict=True)
    # all other plates have 4 channels and will use that specific pipeline
    else:
        info["path_to_pipeline"] = pathlib.Path(
            f"./NF1_analysis_4channel.cppipe"
        ).resolve(strict=True)

# view the dictionary to assess that all info is added correctly
pprint.pprint(plate_info_dictionary, indent=4)


# ## Run analysis pipeline on each plate in parallel
# 
# This cell is not finished to completion due to how long it would take. It is ran in the python file instead.

# In[4]:


cp_parallel.run_cellprofiler_parallel(
    plate_info_dictionary=plate_info_dictionary, run_name=run_name
)

