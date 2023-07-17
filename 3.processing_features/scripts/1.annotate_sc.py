#!/usr/bin/env python
# coding: utf-8

# # Annotate merged single cells with metadata from platemap file for each plate

# ## Import libraries

# In[1]:


import sys
import pathlib
import yaml
import pprint

import pandas as pd
from pycytominer import annotate
from pycytominer.cyto_utils import output

sys.path.append("../utils")
import extraction_utils as sc_utils


# ## Set paths and variables

# In[2]:


# output directory for annotated data
output_dir = pathlib.Path("./data/annotated_data")
output_dir.mkdir(exist_ok=True)

# directory with metadata
metadata_dir = pathlib.Path("../0.download_data/metadata/")

# load in dicionary from yaml file
dictionary_path = pathlib.Path("./plate_info_dictionary.yaml")
with open(dictionary_path) as file:
    plate_info_dictionary = yaml.load(file, Loader=yaml.FullLoader)


# ## Add metadata paths to loaded in dictionary

# In[3]:


# add path to platemaps for each plate 
for plate, _ in plate_info_dictionary.items():
    # since Plate_3_prime has the same platemap as Plate_3, we need an else statement so that we make sure it adds the 
    # path that was given to Plate_3
    if plate != "Plate_3_prime":
        # match the naming format of the plates to the platemap file
        plate_info_dictionary[plate]["platemap_path"] = str(
            pathlib.Path(list(metadata_dir.rglob(f"platemap_NF1_{plate.replace('_', '').lower()}.csv"))[0]).resolve(
                strict=True
            )
        )
    else:
        plate_info_dictionary["Plate_3_prime"]["platemap_path"] = plate_info_dictionary["Plate_3"]["platemap_path"]

# view the dictionary to assess that all info is added correctly
pprint.pprint(plate_info_dictionary, indent=4)


# ## Annotate merged single cells
# 
# **Note:** The path to the annotated file to be used for normalization is adding during this step.

# In[4]:


for plate, info in plate_info_dictionary.items():
    # single_cell_df is the dataframe loaded in from the converted parquet file
    single_cell_df = pd.read_parquet(info["dest_path"])
    platemap_df = pd.read_csv(info["platemap_path"])
    output_file = str(pathlib.Path(f"{output_dir}/{plate}_sc.parquet"))
    # save path to annotated file to dictionary for downstream use
    plate_info_dictionary[plate]["annotated_path"] = output_file
    print(f"Adding annotations to merged single cells for {plate}!")

    # add metadata from platemap file to extracted single cell features
    annotated_df = annotate(
        profiles=single_cell_df,
        platemap=platemap_df,
        join_on=["Metadata_well_position", "Image_Metadata_Well"],
    )

    # rename site column to avoid any issues with identifying the column as metadata over feature
    annotated_df = annotated_df.rename(columns={"Image_Metadata_Site": "Metadata_Site"})

    # move metadata well, single cell count, and site to the front of the df (for easy visualization in python)
    well_column = annotated_df.pop("Metadata_Well")
    singlecell_column = annotated_df.pop("Metadata_number_of_singlecells")
    site_column = annotated_df.pop("Metadata_Site")    

    # insert the columns in specific parts of the dataframe
    annotated_df.insert(2, "Metadata_Well", well_column)
    annotated_df.insert(3, "Metadata_Site", site_column)
    annotated_df.insert(4, "Metadata_number_of_singlecells", singlecell_column)

    # save annotated df as parquet file
    output(
        df=annotated_df,
        output_filename=output_file,
        output_type="parquet",
    )
    print(f"Annotations have been added to {plate} and saved!")


# In[5]:


# print last annotated df to see if annotation occurred
print(annotated_df.shape)
annotated_df.head()


# ## Write updated dictionary to yaml file for use in downstream steps

# In[6]:


with open(dictionary_path, "w") as file:
    yaml.dump(plate_info_dictionary, file)

