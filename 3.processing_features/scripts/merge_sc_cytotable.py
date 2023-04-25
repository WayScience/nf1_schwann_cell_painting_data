#!/usr/bin/env python
# coding: utf-8

# # Merge single cells from CellProfiler outputs using CytoTable

# ## Import libraries

# In[1]:


import sys
import pathlib

# cytotable will merge objects from SQLite file into single cells and save as parquet file
from cytotable import convert, presets

sys.path.append("../utils")
import extraction_utils as sc_utils

# ## Set paths and variables

# In[2]:


# type of file output from CytoTable (currently only parquet)
dest_datatype = "parquet"

# preset configurations based on typical CellProfiler outputs
preset = "cellprofiler_sqlite_pycytominer"
# remove Image_Metadata_Plate from SELECT as this metadata was not extracted from file names
# add Image_Metadata_Site as this is an important metadata when finding where single cells are located
presets.config["cellprofiler_sqlite_pycytominer"][
    "CONFIG_JOINS"
    # create filtered list of image features to be extracted and used for merging tables
    # with the list of image features, this will merge the objects together using the image number,
    # and parent objects to create all single cells (all objetcs associated to one cell)
] = """WITH Per_Image_Filtered AS (
                SELECT
                    Metadata_ImageNumber,
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

# directory where parquet files are saved to
output_dir = "data/converted_data"

# In[3]:


# dictionary with info for the sqlite file from each plate
plate_info_dictionary = {
    "Plate_1": {
        # path to outputed SQLite file
        "source_path": str(
            pathlib.Path(
                "../2.cellprofiler_analysis/analysis_output/Plate_1.sqlite"
            )
        ),
        "dest_path": str(pathlib.Path(f"{output_dir}/Plate_1.parquet")),
    },
    "Plate_2": {
        # path to outputed SQLite file
        "source_path": str(
            pathlib.Path(
                "../2.cellprofiler_analysis/analysis_output/Plate_2.sqlite"
            )
        ),
        # path for merged single cell paraquet file (without annotations)
        "dest_path": str(pathlib.Path(f"{output_dir}/Plate_2.parquet")),
    },
    "Plate_3": {
        # path to outputed SQLite file
        "source_path": str(
            pathlib.Path(
                "../2.cellprofiler_analysis/analysis_output/Plate_3.sqlite"
            )
        ),
        # path for merged single cell paraquet file (without annotations)
        "dest_path": str(pathlib.Path(f"{output_dir}/Plate_3.parquet")),
    },
    "Plate_3_prime": {
        # path to outputed SQLite file
        "source_path": str(
            pathlib.Path(
                "../2.cellprofiler_analysis/analysis_output/Plate_3_prime.sqlite"
            )
        ),
        # path for merged single cell paraquet file (without annotations)
        "dest_path": str(pathlib.Path(f"{output_dir}/Plate_3_prime.parquet")),
    }
}

# ## Merge objects to single cells and convert SQLite to parquet file + add single cell metadata

# In[4]:


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
