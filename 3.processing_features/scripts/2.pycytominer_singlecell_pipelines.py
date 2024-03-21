#!/usr/bin/env python
# coding: utf-8

# ## Perform single-cell pycytominer pipelines
# 
# Following single-cell curation with cytotable, we create single-cell profiles by applying the following steps:
# 
# 1. annotation
# 2. normalization
# 3. feature_selection
# 
# Additionally, we create bulk profiles following feature selection.
# We call this "Cameron's Method".
# 
# 4. Aggregate (to form bulk, after single-cell processing)

# In[1]:


import pathlib
import yaml
import pprint

import pandas as pd

from pycytominer import aggregate, annotate, normalize, feature_select
from pycytominer.cyto_utils import load_profiles, output, infer_cp_features


# In[2]:


# Set constants
feature_select_ops = [
    "variance_threshold",
    "correlation_threshold",
    "blocklist",
    "drop_na_columns"
]

# Columns to remove prior to single-cell aggregation via cameron's method
cameron_unwanted_aggregate_cols = {"Object", "Parent", "Site", "Image"}

# Set paths
output_dir = pathlib.Path("data/single_cell_profiles")
output_dir.mkdir(exist_ok=True)
metadata_dir = pathlib.Path("../0.download_data/metadata/")

# load in plate information
dictionary_path = pathlib.Path("./plate_info_dictionary.yaml")
with open(dictionary_path) as file:
    plate_info_dictionary = yaml.load(file, Loader=yaml.FullLoader)


# In[3]:


# add path to platemaps for each plate
for plate in plate_info_dictionary.keys():
    # since Plate_3_prime has the same platemap as Plate_3,
    # we need an else statement so that we make sure it adds the
    # path that was given to Plate_3
    if plate != "Plate_3_prime":
        # match the naming format of the plates to the platemap file
        plate_info_dictionary[plate]["platemap_path"] = str(
            pathlib.Path(
                list(
                    metadata_dir.rglob(f"platemap_NF1_{plate.replace('_', '').lower()}.csv")
                )[0]
            ).resolve(strict=True)
        )
    else:
        plate_info_dictionary["Plate_3_prime"]["platemap_path"] = (
            plate_info_dictionary["Plate_3"]["platemap_path"]
        )

# view the dictionary to assess that all info is added correctly
pprint.pprint(plate_info_dictionary, indent=4)


# ## Perform single-cell pycytominer pipeline

# In[4]:


for plate, info in plate_info_dictionary.items():
    print(f"Now performing single-cell pycytominer pipeline for {plate}")
    output_annotated_file = str(pathlib.Path(f"{output_dir}/{plate}_sc_annotated.parquet"))
    output_normalized_file = str(pathlib.Path(f"{output_dir}/{plate}_sc_normalized.parquet"))
    output_feature_select_file = str(pathlib.Path(f"{output_dir}/{plate}_sc_feature_selected.parquet"))
    output_aggregated_file = str(pathlib.Path(f"{output_dir}/{plate}_bulk_camerons_method.parquet"))

    # Load single-cell profiles
    single_cell_df = pd.read_parquet(info["dest_path"])

    # Load platemap
    platemap_df = pd.read_csv(info["platemap_path"])

    # Step 1: Annotation
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
        output_filename=output_annotated_file,
        output_type="parquet",
    )

    # set default for samples to use in normalization
    samples = "all"

    # Only for Plate 4, we want to normalize to no siRNA treatment Null cells (controls)
    if plate == "Plate_4":
        samples = "Metadata_Concentration == 0.0 and Metadata_genotype == 'Null'"

    print(f"Performing normalization for {plate} using samples parameter: {samples}")

    # Step 2: Normalization
    normalized_df = normalize(
        profiles=output_annotated_file,
        method="standardize",
        output_file=output_normalized_file,
        output_type="parquet",
        samples=samples,
    )

    # Step 3: Feature selection
    feature_select(
        output_normalized_file,
        operation=feature_select_ops,
        na_cutoff=0,
        output_file=output_feature_select_file,
        output_type="parquet"
    )

    # Step 4: Cameron's method of aggregation
    feature_select_df = load_profiles(output_feature_select_file)
    # Specify metadata columns in aggregation step to ensure they are retained for downstream analysis
    metadata_cols = infer_cp_features(feature_select_df, metadata=True)
    metadata_cols = [x for x in metadata_cols if all(col not in x for col in cameron_unwanted_aggregate_cols)]

    aggregate_df = aggregate(
        population_df=feature_select_df,
        operation="median",
        strata=metadata_cols,
        output_file=output_aggregated_file,
        output_type="parquet"
    )

    print(aggregate_df.shape)

