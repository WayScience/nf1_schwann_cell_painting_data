#!/usr/bin/env python
# coding: utf-8

# ## Normalize merged single cells with standardized method for each plate

# ## Import libraries

# In[1]:


import sys
import pathlib
import os

import pandas as pd
from pycytominer import normalize
from pycytominer.cyto_utils import output

sys.path.append("../utils")
import extraction_utils as sc_utils

# In[2]:


# output directory for normalized data
output_dir = pathlib.Path("./data/normalized_data")
# if directory if doesn't exist, will not raise error if it already exists
os.makedirs(output_dir, exist_ok=True)

# dictionary with each run for the cell type
plate_info_dictionary = {
    "Plate_1": {
        # path to parquet file from annotate function
        "annotated_path": str(pathlib.Path("./data/annotated_data/Plate_1_sc.parquet"))
    },
    "Plate_2": {
        # path to parquet file from annotate function
        "annotated_path": str(pathlib.Path("./data/annotated_data/Plate_2_sc.parquet"))
    },
    "Plate_3": {
        # path to parquet file from annotate function
        "annotated_path": str(pathlib.Path("./data/annotated_data/Plate_3_sc.parquet"))
    },
    "Plate_3_prime": {
        # path to parquet file from annotate function
        "annotated_path": str(pathlib.Path("./data/annotated_data/Plate_3_prime_sc.parquet"))
    }
}

# In[3]:


# process each run
for plate, info in plate_info_dictionary.items():
    annotated_df = pd.read_parquet(info["annotated_path"])
    output_file = str(pathlib.Path(f"{output_dir}/{plate}_sc_norm.parquet"))
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
