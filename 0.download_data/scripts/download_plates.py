#!/usr/bin/env python
# coding: utf-8

# # Download NF1 datasets from Figshare

# ## Import libraries

# In[1]:


import pathlib
import download_figshare as df


# ## Set paths and variables for each plate

# In[2]:


# Plate 1
figshare_id1 = "22233292/versions/1"
output_folder1 = "Plate_1_zip"
output_dir1 = pathlib.Path("Plate_1")

# Plate 2
figshare_id2 = "22233700/versions/3"
output_folder2 = "Plate_2_zip"
output_dir2 = pathlib.Path("Plate_2")

# figshare url for both plates
figshare_url = "https://figshare.com/ndownloader/articles/"

# metadata folder for metadata files from both plates to be moved into
metadata_dir = pathlib.Path("metadata")


# # Download files for Plate 1

# In[3]:


df.download_figshare(
    figshare_id=figshare_id1,
    output_file=output_folder1,
    output_dir=output_dir1,
    metadata_dir=metadata_dir,
    figshare_url=figshare_url,
)


# ## Download files for Plate 2

# In[4]:


df.download_figshare(
    figshare_id=figshare_id2,
    output_file=output_folder2,
    output_dir=output_dir2,
    metadata_dir=metadata_dir,
    figshare_url=figshare_url,
)

