#!/usr/bin/env python
# coding: utf-8

# # Download NF1 datasets from Figshare

# ## Import libraries

# In[1]:


import os
import pathlib
import shutil

import sys
sys.path.append("../")
from utils import download_figshare as downfig

# ## Set constant paths/variables

# In[2]:


# figshare url for both plates
figshare_url = "https://figshare.com/ndownloader/articles/"

# metadata folder for metadata files from both plates to be moved into
metadata_dir = pathlib.Path("metadata")

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
        "output_dir": pathlib.Path("./Plate_1"),
    },
    "Plate_2": {
        "figshare_id": "22233700",
        "version_number": "4",
        "output_folder": "Plate_2_zip",
        "output_dir": pathlib.Path("./Plate_2"),
    },
    # these plates are combined due to the figsahre project containing zip files with the images for each
    # plate that will need to be extracted in a second step
    "Plates_3_and_3_prime": {
        "figshare_id": "22592890",
        "version_number": "1",
        "output_folder": "Plates_3_zip",
        "output_dir": pathlib.Path("./Plates_3_and_3_prime"),
    },
}

# ## Download files for all plates
# 
# **Note:** In the case of the NF1 Schwann Cell Project, the items on figshare are downloaded as zip files so we will have the `unzip_download` parameter turned on to extract the items from the zip file into the respective plate directory.

# In[4]:


for _, info in download_plates_info_dictionary.items():
    # set the parameters for the function as variables based on the plate dictionary info
    figshare_id = str(
        info["figshare_id"] + "/versions/" + info["version_number"]
    )
    output_folder = info["output_folder"]
    output_dir = info["output_dir"]

    # download images and metadata for both plates
    downfig.download_figshare(
        figshare_id=figshare_id,
        output_file=output_folder,
        output_dir=output_dir,
        metadata_dir=metadata_dir,
        figshare_url=figshare_url,
        unzip_download="True",
    )

# ## Extract images from extracted zip file from figshare download

# In[5]:


# this dictionary contains the paths to the extracted zip file from the previous step for each plate
# and the path to the directory for the images
zip_images_dictionary ={
    "Plate_3": {
        "path_to_zip_file": pathlib.Path("./Plates_3_and_3_prime/plate_3.zip"),
        "extraction_path": pathlib.Path("./Plate_3"),
    },
    "Plate_3_prime": {
        "path_to_zip_file": pathlib.Path("./Plates_3_and_3_prime/plate_3_prime.zip"),
        "extraction_path": pathlib.Path("./Plate_3_prime"),
    },
}

for plate, info in zip_images_dictionary.items():
    # set the parameters for the function as variables based on the plate dictionary info
    path_to_zip_file = info["path_to_zip_file"]
    extraction_path = info["extraction_path"]
    print(f"Starting extraction on {plate} zip file!")

    # download images and metadata for both plates
    downfig.extract_zip_from_Figshare(
        path_to_zip_file=path_to_zip_file,
        extraction_path=extraction_path,
    )

# remove the parent directory with the zip files as we have moved all the images
parent_directory = os.path.dirname(path_to_zip_file)
shutil.rmtree(parent_directory)
print(f"The directory containing zip files from Figshare has been deleted as the files have been extracted!")

