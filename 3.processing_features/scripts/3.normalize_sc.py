#!/usr/bin/env python
# coding: utf-8

# ## Normalize merged single cells with standardized method for each plate

# ## Import libraries

# In[1]:


import pathlib
import yaml
import pprint

import pandas as pd
from pycytominer import normalize
from pycytominer.cyto_utils import output


# ## Set paths and load in dictionary from annotated run

# In[2]:


# output directory for normalized data
output_dir = pathlib.Path("./data/normalized_data")
output_dir.mkdir(exist_ok=True)

# load in dicionary from yaml file
dictionary_path = pathlib.Path("./plate_info_dictionary.yaml")
with open(dictionary_path) as file:
    plate_info_dictionary = yaml.load(file, Loader=yaml.FullLoader)

# view the dictionary to assess that all info is added correctly
pprint.pprint(plate_info_dictionary)


# ## Normalize annotated bulk profiles from each plate

# In[3]:


# process each run
for plate, info in plate_info_dictionary.items():
    annotated_df = pd.read_parquet(info["bulk_annotated_path"])
    # set output path and add to the dictionary
    output_file = str(pathlib.Path(f"{output_dir}/{plate}_bulk_norm.parquet"))
    # save path to normalized file to dictionary for downstream use
    plate_info_dictionary[plate]["bulk_normalized_path"] = output_file
    print(f"Normalizing annotated bulk profiles for {plate}!")

    # normalize annotated data
    normalized_df = normalize(
            # df with annotated raw merged single cell features
            profiles=annotated_df,
            # normalization method used
            method="standardize"
    )

    # save df as parquet file
    output(
        df=normalized_df,
        output_filename=output_file,
        output_type="parquet",
    )
    print(f"Bulk profiles have been normalized for {plate} and saved!")


# ## Normalize annotated single cells from each plate
# 
# **Note:** Path to normalized data for each plate is added to the dictionary in this step to be used during feature selection.

# In[4]:


# process each run
for plate, info in plate_info_dictionary.items():
    annotated_df = pd.read_parquet(info["annotated_path"])
    # set output path and add to the dictionary
    output_file = str(pathlib.Path(f"{output_dir}/{plate}_sc_norm.parquet"))
    # save path to normalized file to dictionary for downstream use
    plate_info_dictionary[plate]["normalized_path"] = output_file
    print(f"Normalizing annotated merged single cells for {plate}!")

    # normalize annotated data
    normalized_df = normalize(
            # df with annotated raw merged single cell features
            profiles=annotated_df,
            # normalization method used
            method="standardize"
    )

    # save df as parquet file
    output(
        df=normalized_df,
        output_filename=output_file,
        output_type="parquet",
    )
    print(f"Single cells have been normalized for {plate} and saved!")


# In[5]:


# print last normalized df to see if looks like normalization has occurred
print(normalized_df.shape)
normalized_df.head()


# ## Write updated dictionary to yaml file for use in downstream steps

# In[6]:


with open(dictionary_path, 'w') as file:
    yaml.dump(plate_info_dictionary, file)

