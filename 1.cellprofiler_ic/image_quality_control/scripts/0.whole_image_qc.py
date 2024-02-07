#!/usr/bin/env python
# coding: utf-8

# # Run whole image QC pipeline in CellProfiler
# 

# ## Import libraries

# In[1]:


import pathlib
import pprint

import sys

sys.path.append("../../utils")
import cp_parallel


# ## Set paths and variables

# In[2]:


# set the run type for the parallelization
run_name = "quality_control"

# set path for pipeline for illumination correction
path_to_pipeline = pathlib.Path("../pipelines/whole_image_qc.cppipe").resolve(strict=True)

# set main output dir for all plates if it doesn't exist
output_dir = pathlib.Path("./qc_results")
output_dir.mkdir(exist_ok=True)

# directory where images are located within folders
images_dir = pathlib.Path("../../0.download_data")

# list for plate names based on folders to use to create dictionary
plate_names = []
# iterate through 0.download_data and append plate names from folder names that contain image data from that plate
for file_path in images_dir.iterdir():
    if str(file_path.stem).startswith("Plate"):
        plate_names.append(str(file_path.stem))

print(plate_names)
print("There are a total of", len(plate_names), "plates. The names of the plates are:")
for plate in plate_names:
    print(plate)


# ## Generate dictionary with plate info to run CellProfiler

# In[3]:


# create plate info dictionary with all parts of the CellProfiler CLI command to run in parallel
plate_info_dictionary = {
    name: {
        "path_to_images": pathlib.Path(list(images_dir.rglob(name))[0]).resolve(
            strict=True
        ),
        "path_to_output": pathlib.Path(f"{output_dir}/{name}"),
        "path_to_pipeline": path_to_pipeline,

    }
    for name in plate_names if not name=='Plate_1' and not name=='Plate_2' # Do not include pilot datasets
}

# view the dictionary to assess that all info is added correctly
pprint.pprint(plate_info_dictionary, indent=4)


# ## Run QC pipeline in CellProfiler

# In[ ]:


cp_parallel.run_cellprofiler_parallel(
    plate_info_dictionary=plate_info_dictionary, run_name=run_name
)

