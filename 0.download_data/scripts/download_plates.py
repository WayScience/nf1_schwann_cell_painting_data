#!/usr/bin/env python
# coding: utf-8

# # Download NF1 datasets from Figshare

# ## Import libraries

# In[1]:


import pathlib
from utils.download_figshare import download_figshare


# ## Set constant paths/variables

# In[2]:


# figshare url for both plates
figshare_url = "https://figshare.com/ndownloader/articles/"

# metadata folder for metadata files from both plates to be moved into
metadata_dir = pathlib.Path("metadata")

# Since the Figshare download is a zip file for the NF1 data, we have to have the unzip_file parameter turned on
unzip_files = True


# ## Set dictionary with specific path/variables for each plate

# In[3]:


download_plates_info_dictionary = {
    "Plate_1": {
        "figshare_id": "22233292",
        "version_number": "1",
        "output_folder": "Plate_1_zip",
        "output_dir": pathlib.Path("Plate_1"),
    },
    "Plate_2": {
        "figshare_id": "22233700",
        "version_number": "3",
        "output_folder": "Plate_2_zip",
        "output_dir": pathlib.Path("Plate_2"),
    },
}


# ## Download files for both plates

# In[4]:


for plate in download_plates_info_dictionary:
    # Access the plate info stored in the dictionary
    plate_info = download_plates_info_dictionary[plate]
    figshare_id = str(
        plate_info["figshare_id"] + "/versions/" + plate_info["version_number"]
    )
    output_folder = plate_info["output_folder"]
    output_dir = plate_info["output_dir"]

    download_figshare(
        figshare_id=figshare_id,
        output_file=output_folder,
        output_dir=output_dir,
        metadata_dir=metadata_dir,
        figshare_url=figshare_url,
        unzip_files=unzip_files,
    )
