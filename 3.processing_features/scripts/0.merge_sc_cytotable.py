#!/usr/bin/env python
# coding: utf-8

# # Merge single cells from CellProfiler outputs using CytoTable

# ## Import libraries

# In[1]:


import sys
import pathlib
import yaml
import pprint
import pandas as pd

# cytotable will merge objects from SQLite file into single cells and save as parquet file
from cytotable import convert, presets

sys.path.append("../utils")
import extraction_utils as sc_utils


# ## Set paths and variables

# In[2]:


# type of file output from CytoTable (currently only parquet)
dest_datatype = "parquet"

# set main output dir for all parquet files
output_dir = pathlib.Path("./data/converted_data/")
output_dir.mkdir(exist_ok=True)

# directory where SQLite files are located
sqlite_dir = pathlib.Path("../2.cellprofiler_analysis/analysis_output/")

# list for plate names based on folders to use to create dictionary
plate_names = []

# iterate through 0.download_data and append plate names from folder names
# that contain image data from that plate
# (Note, you must first run `0.download_data/download_plates.ipynb`)
for file_path in pathlib.Path("../0.download_data/").iterdir():
    if str(file_path.stem).startswith("Plate"):
        plate_names.append(str(file_path.stem))
        
plate_names


# In[3]:


# preset configurations based on typical CellProfiler outputs
preset = "cellprofiler_sqlite_pycytominer"
# remove Image_Metadata_Plate from SELECT as this metadata was not extracted from file names
# add Image_Metadata_Site as this is an important metadata when finding where single cells are located
presets.config["cellprofiler_sqlite_pycytominer"][
    "CONFIG_JOINS"
    # create filtered list of image features to be extracted and used for merging tables
    # with the list of image features, this will merge the objects together using the image number,
    # and parent objects to create all single cells (all objects associated to one cell)
] = """WITH Per_Image_Filtered AS (
                SELECT
                    Metadata_ImageNumber,
                    Image_Metadata_Plate,
                    Image_Metadata_Well,
                    Image_Metadata_Site
                FROM
                    read_parquet('per_image.parquet')
                )
            SELECT
                *
            FROM
                Per_Image_Filtered AS per_image
            LEFT JOIN read_parquet('per_cytoplasm.parquet') AS per_cytoplasm ON
                per_cytoplasm.Metadata_ImageNumber = per_image.Metadata_ImageNumber
            LEFT JOIN read_parquet('per_cells.parquet') AS per_cells ON
                per_cells.Metadata_ImageNumber = per_cytoplasm.Metadata_ImageNumber
                AND per_cells.Metadata_Cells_Number_Object_Number = per_cytoplasm.Metadata_Cytoplasm_Parent_Cells
            LEFT JOIN read_parquet('per_nuclei.parquet') AS per_nuclei ON
                per_nuclei.Metadata_ImageNumber = per_cytoplasm.Metadata_ImageNumber
                AND per_nuclei.Metadata_Nuclei_Number_Object_Number = per_cytoplasm.Metadata_Cytoplasm_Parent_Nuclei
                """


# ## Create dictionary with info for each plate
# 
# **Note:** All paths must be string to use with CytoTable.

# In[4]:


# create plate info dictionary with all parts of the CellProfiler CLI command to run in parallel
plate_info_dictionary = {
    name: {
        "source_path": str(pathlib.Path(
            list(sqlite_dir.rglob(f"{name}_nf1_analysis.sqlite"))[0]
        ).resolve(strict=True)),
        "dest_path": str(pathlib.Path(f"{output_dir}/{name}.parquet")),
    }
    for name in plate_names
}

# view the dictionary to assess that all info is added correctly
pprint.pprint(plate_info_dictionary, indent=4)


# ## Merge objects to single cells and convert SQLite to parquet file + add single cell metadata

# In[5]:


# run through each run with each set of paths based on dictionary
for plate, info in plate_info_dictionary.items():
    source_path = info["source_path"]
    dest_path = info["dest_path"]
    
    print(f"Performing merge single cells and conversion on {plate}!")

    # merge single cells and output as parquet file
    convert(
        source_path=source_path,
        dest_path=dest_path,
        dest_datatype=dest_datatype,
        preset=preset,
    )
    print(f"Merged and converted {pathlib.Path(dest_path).name}!")

    # add single cell count per well as metadata column to parquet file and save back to same path
    sc_utils.add_sc_count_metadata_file(
        data_path=dest_path, well_column_name="Image_Metadata_Well", file_type="parquet"
    )
    
    print(f"Added single cell count as metadata to {pathlib.Path(dest_path).name}!")


# ### Check if converted data looks correct

# In[6]:


converted_df = pd.read_parquet(plate_info_dictionary["Plate_4"]["dest_path"])

print(converted_df.shape)
converted_df.head()


# ## Write dictionary to yaml file for use in downstream steps

# In[7]:


dictionary_path = pathlib.Path("./plate_info_dictionary.yaml")
with open(dictionary_path, 'w') as file:
    yaml.dump(plate_info_dictionary, file)

