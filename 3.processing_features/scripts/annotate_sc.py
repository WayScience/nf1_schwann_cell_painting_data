#!/usr/bin/env python
# coding: utf-8

# # Annotate merged single cells with metadata from platemap file for each plate

# ## Import libraries

# In[1]:


import sys
import pathlib
import os

import pandas as pd
from pycytominer import annotate
from pycytominer.cyto_utils import output

sys.path.append("../utils")
import extraction_utils as sc_utils

# ## Set paths and variables

# In[2]:


# output directory for annotated data
output_dir = pathlib.Path("./data/annotated_data")
# if directory if doesn't exist, will not raise error if it already exists
os.makedirs(output_dir, exist_ok=True)

# dictionary with each run for the cell type
plate_info_dictionary = {
    "Plate_1": {
        # path to parquet file from convert function
        "single_cell_path": str(pathlib.Path("./data/converted_files/Plate_1.parquet")),
        "platemap_path": str(pathlib.Path("../0.download_data/metadata/platemap_NF1_plate1.csv"))
    },
    "Plate_2": {
        # path to parquet file from convert function
        "single_cell_path": str(pathlib.Path("./data/converted_files/Plate_2.parquet")),
        "platemap_path": str(pathlib.Path("../0.download_data/metadata/platemap_NF1_plate2.csv"))
    },
    "Plate_3": {
        # path to parquet file from convert function
        "single_cell_path": str(pathlib.Path("./data/converted_files/Plate_3.parquet")),
        # both plate 3 and plate 3 prime have the same plate map file 
        "platemap_path": str(pathlib.Path("../0.download_data/metadata/platemap_NF1_plate3.csv"))
    },
    "Plate_3_prime": {
        # path to parquet file from convert function
        "single_cell_path": str(pathlib.Path("./data/converted_files/Plate_3_prime.parquet")),
        # both plate 3 and plate 3 prime have the same plate map file
        "platemap_path": str(pathlib.Path("../0.download_data/metadata/platemap_NF1_plate3.csv"))
    },
}

# ## Annotate merged single cells

# In[3]:


for plate, info in plate_info_dictionary.items():
    # load in parquet file as df to use in annotate function
    single_cell_df = pd.read_parquet(info["single_cell_path"])
    platemap_df = pd.read_csv(info["platemap_path"])
    output_file = str(pathlib.Path(f"{output_dir}/{plate}_sc.parquet"))
    print(f"Adding annotations to merged single cells for {plate}!")

    # add metadata from platemap file to extracted single cell features
    annotated_df = annotate(
        profiles=single_cell_df,
        platemap=platemap_df,
        join_on=["Metadata_well_position", "Image_Metadata_Well"],
    )

    # move metadata well and single cell count to the front of the df (for easy visualization in python)
    well_column = annotated_df.pop("Metadata_Well")
    singlecell_column = annotated_df.pop("Metadata_number_of_singlecells")
    # insert the column as the second index column in the dataframe
    annotated_df.insert(1, "Metadata_Well", well_column)
    annotated_df.insert(2, "Metadata_number_of_singlecells", singlecell_column)

    # save annotated df as parquet file
    output(
        df=annotated_df,
        output_filename=output_file,
        output_type="parquet",
    )
    print(f"Annotations have been added to {plate} and saved!")

# In[4]:


# print last annotated df to see if annotation occurred
print(annotated_df.shape)
annotated_df.head()
