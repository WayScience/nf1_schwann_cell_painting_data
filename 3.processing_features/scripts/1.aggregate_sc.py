#!/usr/bin/env python
# coding: utf-8

# # Perform aggregation on all plates to output bulk profiles

# ## Import libraries

# In[1]:


import pathlib
import yaml
import pprint

import pandas as pd
from pycytominer import aggregate
from pycytominer.cyto_utils import output


# ## Set paths and variables

# In[2]:


# output directory for annotated data
output_dir = pathlib.Path("./data/aggregated_data")
output_dir.mkdir(exist_ok=True)

# load in dicionary from yaml file
dictionary_path = pathlib.Path("./plate_info_dictionary.yaml")
with open(dictionary_path) as file:
    plate_info_dictionary = yaml.load(file, Loader=yaml.FullLoader)

# view the dictionary to assess that all info is added correctly
pprint.pprint(plate_info_dictionary, indent=4)


# ## Peform aggregation
# 
# **Note:** We use the default operation of `median` for aggregating the single cell data.

# In[3]:


for plate, info in plate_info_dictionary.items():
    # single_cell_df is the dataframe loaded in from the converted parquet file
    single_cell_df = pd.read_parquet(info["dest_path"])
    output_file = str(pathlib.Path(f"{output_dir}/{plate}_bulk.parquet"))
    # save path to annotated file to dictionary for downstream use
    plate_info_dictionary[plate]["bulk_path"] = output_file
    print(f"Performing aggregation on {plate}!")

    # perform median aggregation (default) to ouput bulk features
    aggregate_df = aggregate(
        population_df=single_cell_df, strata=["Image_Metadata_Plate", "Image_Metadata_Well"]
    )

    # save aggregated df as parquet file
    output(
        df=aggregate_df,
        output_filename=output_file,
        output_type="parquet",
    )
    print(f"The bulk profile for {plate} has been created and saved!")


# In[4]:


# print last aggregate df to see if annotation occurred
print(aggregate_df.shape)
aggregate_df.head()


# ## Write updated dictionary to yaml file for use in downstream steps

# In[5]:


with open(dictionary_path, "w") as file:
    yaml.dump(plate_info_dictionary, file)

