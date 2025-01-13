#!/usr/bin/env python
# coding: utf-8

# # Correct illumination and save images for each plate using CellProfiler Parallel

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
run_name = "illum_correction"

# Directory with pipelines
pipeline_dir = pathlib.Path("./pipelines/").resolve(strict=True)

# set main output dir for all plates
output_dir = pathlib.Path("./Corrected_Images")
output_dir.mkdir(exist_ok=True)

# directory where images are located within folders
images_dir = pathlib.Path("../0.download_data/")

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
        "path_to_images": pathlib.Path(list(images_dir.rglob(name))[0]).resolve(
            strict=True
        ),
        "path_to_output": pathlib.Path(f"{output_dir}/Corrected_{name}"),
    }
    for name in plate_names
    if not any(
        pathlib.Path(f"{output_dir}/Corrected_{name}").glob("*")
    )  # only add plates that have not been processed yet
}

# iterate over the dictionary and add the path_to_pipeline specific for each plate
for name, info in plate_info_dictionary.items():
    # only plates 1 and 2 have 3 channels so these are the only plates that use this path
    if name == "Plate_1" or name == "Plate_2":
        info["path_to_pipeline"] = pathlib.Path(
            f"{pipeline_dir}/NF1_illum_3channel.cppipe"
        ).resolve(strict=True)
    # all other plates have 4 channels and will use that specific pipeline
    else:
        info["path_to_pipeline"] = pathlib.Path(
            f"{pipeline_dir}/NF1_illum_4channel.cppipe"
        ).resolve(strict=True)

# view the dictionary to assess that all info is added correctly
pprint.pprint(plate_info_dictionary, indent=4)


# ## Run illumination correction pipeline on each plate in parallel
# 
# In this notebook, we do not run the cells to completion as we prefer to run the notebooks as nbconverted python files due to better stability.

# In[ ]:


cp_parallel.run_cellprofiler_parallel(
    plate_info_dictionary=plate_info_dictionary, run_name=run_name
)

