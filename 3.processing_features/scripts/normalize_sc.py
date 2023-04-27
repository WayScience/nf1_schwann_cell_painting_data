#!/usr/bin/env python
# coding: utf-8

# ## Normalize merged single cells with standardized method for each plate

# ## Import libraries

# In[1]:


import sys
import pathlib
import os
import yaml
import json

import pandas as pd
from pycytominer import normalize
from pycytominer.cyto_utils import output


# In[2]:


# output directory for normalized data
output_dir = pathlib.Path("./data/normalized_data")
# if directory if doesn't exist, will not raise error if it already exists
os.makedirs(output_dir, exist_ok=True)

# load in dicionary from yaml file
dictionary_path = pathlib.Path("./plate_info_dictionary.yaml")
with open(dictionary_path) as file:
    plate_info_dictionary = yaml.load(file, Loader=yaml.FullLoader)

# view the dictionary to confirm all info is included to use for normalization
print(json.dumps(plate_info_dictionary, indent=4))


# In[3]:


# process each run
for plate, info in plate_info_dictionary.items():
    annotated_df = pd.read_parquet(info["annotated_path"])
    output_file = str(pathlib.Path(f"{output_dir}/{plate}_sc_norm.parquet"))
    # save path to annotated file to dictionary for downstream use
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


# In[4]:


# print last normalized df to see if looks like normalization has occurred
print(normalized_df.shape)
normalized_df.head()


# ## Write updated dictionary to yaml file for use in downstream steps

# In[5]:


with open(dictionary_path, 'w') as file:
    yaml.dump(plate_info_dictionary, file)

