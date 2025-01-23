#!/usr/bin/env python
# coding: utf-8

# ## Perform traditional bulk pycytominer pipeline
# 
# Following single-cell curation with cytotable, we create bulk profiles by applying the following steps:
# 
# 1. aggregation
# 2. annotation
# 3. normalization
# 4. feature_selection

# In[1]:


import pathlib
import yaml
import pprint

import pandas as pd

from pycytominer import aggregate, annotate, normalize, feature_select
from pycytominer.cyto_utils import load_profiles, output


# In[2]:


# Set constants
feature_select_ops = [
    "variance_threshold",
    "correlation_threshold",
    "blocklist",
    "drop_na_columns",
]

# Set paths
output_dir = pathlib.Path("data/bulk_profiles")
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
                    metadata_dir.rglob(
                        f"platemap_NF1_{plate.replace('_', '').lower()}.csv"
                    )
                )[0]
            ).resolve(strict=True)
        )
    else:
        plate_info_dictionary["Plate_3_prime"]["platemap_path"] = plate_info_dictionary[
            "Plate_3"
        ]["platemap_path"]

# view the dictionary to assess that all info is added correctly
pprint.pprint(plate_info_dictionary, indent=4)


# ## Perform pycytominer pipeline

# In[4]:


for plate, info in plate_info_dictionary.items():
    print(f"Now performing pycytominer pipeline for {plate}")
    output_aggregated_file = str(pathlib.Path(f"{output_dir}/{plate}_bulk.parquet"))
    output_annotated_file = str(
        pathlib.Path(f"{output_dir}/{plate}_bulk_annotated.parquet")
    )
    output_normalized_file = str(
        pathlib.Path(f"{output_dir}/{plate}_bulk_normalized.parquet")
    )
    output_feature_select_file = str(
        pathlib.Path(f"{output_dir}/{plate}_bulk_feature_selected.parquet")
    )

    # Load single-cell profiles
    single_cell_df = pd.read_parquet(info["dest_path"])

    # Load platemap
    platemap_df = pd.read_csv(info["platemap_path"])

    # Step 1: Aggregation
    aggregate_df = aggregate(
        population_df=single_cell_df,
        operation="median",
        strata=["Image_Metadata_Plate", "Image_Metadata_Well"],
    )

    print("Aggregated dataframe shape", aggregate_df.shape)

    output(
        df=aggregate_df,
        output_filename=output_aggregated_file,
        output_type="parquet",
    )

    # Step 2: Annotation
    annotated_df = annotate(
        profiles=output_aggregated_file,
        platemap=platemap_df,
        join_on=["Metadata_well_position", "Image_Metadata_Well"],
    )

    # For only plates 3 and 3 prime, remove any rows with HET due to contamination
    if plate in ["Plate_3", "Plate_3_prime"]:
        # Filter single-cell profiles, removing HET genotype
        annotated_df = annotated_df[annotated_df["Metadata_genotype"] != "HET"]
        print("HET cells have been removed from", plate)

    print("Annotated dataframe shape", annotated_df.shape)

    # use output to the updated annotated file
    output(
        df=annotated_df,
        output_filename=output_annotated_file,
        output_type="parquet",
    )

    # set default for samples to use in normalization and feature selection
    samples = "all"

    # Only for Plate 4, we want to normalize to no siRNA treatment Null and WT cells (controls)
    if plate == "Plate_4":
        samples = "Metadata_Concentration == 0.0 and (Metadata_genotype == 'Null' or Metadata_genotype == 'WT')"

    # Only for Plate 6, we want to normalize to iNFixion institution and Null and WT cells 
    # to keep consistent with how the other plates are normalized (same cell line)
    if plate == "Plate_6":
        samples = "Metadata_Institution == 'iNFixion' and (Metadata_genotype == 'Null' or Metadata_genotype == 'WT')"

    # Step 3: Normalization
    normalized_df = normalize(
        profiles=annotated_df,
        method="standardize",
        samples=samples,
    )

    print("Normalized dataframe shape", normalized_df.shape)

    output(
        df=normalized_df,
        output_filename=output_normalized_file,
        output_type="parquet",
    )

    # Step 4: Feature selection
    feature_select_df = feature_select(
        normalized_df,
        operation=feature_select_ops,
        na_cutoff=0,
        samples=samples,
    )

    print("Feature selected dataframe shape", feature_select_df.shape)

    output(
        df=feature_select_df,
        output_filename=output_feature_select_file,
        output_type="parquet",
    )


# In[5]:


# Check output file
test_df = load_profiles(output_feature_select_file)

print(test_df.shape)
test_df.head(2)

