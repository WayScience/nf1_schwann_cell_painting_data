#!/usr/bin/env python
# coding: utf-8

# # Download NF1 datasets from Figshare

# ## Import libraries

# In[1]:


import pathlib

import sys
sys.path.append("../")
from utils import download_figshare as downfig


# ## Set constant paths/variables

# In[2]:


# figshare url for both plates
figshare_url = "https://figshare.com/ndownloader/articles/"

# metadata folder for metadata files from both plates to be moved into
metadata_dir = pathlib.Path("metadata")

# Since the Figshare download is a zip file for the NF1 data, we have to have the unzip_file parameter turned on
unzip_files = True


# ## Set dictionary with specific path/variables for each plate
# 
# **Note:** You are able to see the correct URL for the plate by copying the link from the `Download all` button on the item (term used for dataset/plate) from the NF1 Schwann Cell Genotype Cell Painting Assay project. As well, there are mutliple versions of this dataset due to correcting the number of images and the metadata files.

# In[3]:


# since we are dealing with zip files, we use the optional parameter `output_dir` where we 
# specify where to extact the files to
download_plates_info_dictionary = {
    "Plate_1": {
        "figshare_id": "22233292",
        "version_number": "2",
        "output_folder": "Plate_1_zip",
        "output_dir": pathlib.Path("Plate_1"),
    },
    "Plate_2": {
        "figshare_id": "22233700",
        "version_number": "4",
        "output_folder": "Plate_2_zip",
        "output_dir": pathlib.Path("Plate_2"),
    },
}


# ## Download files for both plates

# In[4]:


for plate in download_plates_info_dictionary:
    # access the plate info stored in the dictionary
    plate_info = download_plates_info_dictionary[plate]
    # set the parameters for the function as variables based on the plate dictionary info
    figshare_id = str(
        plate_info["figshare_id"] + "/versions/" + plate_info["version_number"]
    )
    output_folder = plate_info["output_folder"]
    output_dir = plate_info["output_dir"]

    # download images and metadata for both plates
    downfig.download_figshare(
        figshare_id=figshare_id,
        output_file=output_folder,
        output_dir=output_dir,
        metadata_dir=metadata_dir,
        figshare_url=figshare_url,
        unzip_files=unzip_files,
    )

