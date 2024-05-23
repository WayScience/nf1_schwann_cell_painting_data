#!/usr/bin/env python
# coding: utf-8

# # Generate UMAP coordinates for each plate

# ## Import libraries

# In[1]:


import glob
import pathlib
import pandas as pd
import umap

from pycytominer import feature_select
from pycytominer.cyto_utils import infer_cp_features


# ## Set constants

# In[2]:


# Set constants
umap_random_seed = 0
umap_n_components = 2

output_dir = pathlib.Path("results")
output_dir.mkdir(parents=True, exist_ok=True)


# ## Create list of paths to feature selected data per plate

# In[3]:


# Set input paths
data_dir = pathlib.Path("../../../3.processing_features/data/single_cell_profiles/")

# Select only the feature selected files
file_suffix = "*sc_feature_selected.parquet"

# Obtain file paths for all feature selected plates
fs_files = glob.glob(f"{data_dir}/{file_suffix}")
fs_files


# In[4]:


# Load feature data into a dictionary, keyed on plate name
cp_dfs = {x.split("/")[-1]: pd.read_parquet(x) for x in fs_files}

# Print out useful information about each dataset
print(cp_dfs.keys())
[cp_dfs[x].shape for x in cp_dfs]


# ## Generate UMAP coordinates for each plate
# 
# **Note:** Only metadata that is common between plates are included in final data frame.

# In[5]:


desired_columns = ["Metadata_Plate","Metadata_Well", "Metadata_Site", "Metadata_number_of_singlecells", "Metadata_genotype"]

# Fit UMAP features per dataset and save
for plate in cp_dfs:
    plate_name = pathlib.Path(plate).stem
    print("UMAP embeddings being generated for", plate_name)

     # Make sure to reinitialize UMAP instance per plate
    umap_fit = umap.UMAP(
        random_state=umap_random_seed,
        n_components=umap_n_components
    )

    # Make sure NA columns have been removed
    cp_df = cp_dfs[plate]
    cp_df = feature_select(
        cp_df,
        operation="drop_na_columns",
        na_cutoff=0
    )

    # Make sure that the Plate_3_prime has correct name in Metadata_Plate column
    if plate_name.replace("_sc_feature_selected", "") == "Plate_3_prime":
        cp_df["Metadata_Plate"] = "Plate_3_prime"

    # Remove rows with genotype HET for Plate_5
    if plate_name.replace("_sc_feature_selected", "") == "Plate_5":
        cp_df = cp_df[cp_df["Metadata_genotype"] != "HET"]
    
    # Process cp_df to separate features and metadata
    cp_features = infer_cp_features(cp_df)
    meta_features = infer_cp_features(cp_df, metadata=True)
    filtered_meta_features = [feature for feature in meta_features if feature in desired_columns]
    
    # Fit UMAP and convert to pandas DataFrame
    embeddings = pd.DataFrame(
        umap_fit.fit_transform(cp_df.loc[:, cp_features]),
        columns=[f"UMAP{x}" for x in range(0, umap_n_components)]
    )
    print(embeddings.shape)
    
    # Combine with metadata
    cp_umap_with_metadata_df = pd.concat([
        cp_df.loc[:, filtered_meta_features].reset_index(drop=True),
        embeddings
    ], axis=1)
    
    # randomize the rows of the dataframe to plot the order of the data evenly
    cp_umap_with_metadata_df = cp_umap_with_metadata_df.sample(frac=1, random_state=0)

    # Generate output file and save
    output_umap_file = pathlib.Path(output_dir, f"UMAP_{plate_name}.tsv")
    cp_umap_with_metadata_df.to_csv(output_umap_file, index=False, sep="\t")


# In[6]:


# Print an example output file
print(cp_umap_with_metadata_df.shape)
cp_umap_with_metadata_df.head()


# In[7]:


# Set input paths
data_dir = pathlib.Path("../../../3.processing_features/data/single_cell_profiles/")

# Select only the feature selected files
fs_suffix = "*sc_feature_selected.parquet"

# Obtain file paths for all feature selected plates
fs_files = glob.glob(f"{data_dir}/{fs_suffix}")
fs_files


# In[8]:


# Select file paths for plates 5, 3, and 3 prime only
selected_plates = ["Plate_5", "Plate_3", "Plate_3_prime", "Plate_4"]

# Filter and concatenate the selected plates
selected_dfs = []
for file_path in fs_files:
    plate_name = pathlib.Path(file_path).stem.replace("_sc_feature_selected", "")

    # Only read in selected plates
    if plate_name in selected_plates:
        df = pd.read_parquet(file_path)

        # Update Metadata_Plate for Plate_3_prime
        if plate_name == "Plate_3_prime":
            df["Metadata_Plate"] = "Plate_3_prime"

        # For Plate_4, only include rows where Metadata_siRNA is "None"
        if plate_name == "Plate_4":
            # Fill NaN values in "Metadata_siRNA" column with "No Construct"
            df["Metadata_siRNA"].fillna("No Construct", inplace=True)

            # Filter out rows where "Metadata_siRNA" is "No Construct"
            df = df[df["Metadata_siRNA"] == "No Construct"]

        selected_dfs.append(df)


# In[9]:


# Get the column names of all DataFrames in selected_dfs
column_sets = [set(df.columns) for df in selected_dfs]

# Find the common column names across all DataFrames
common_columns = list(set.intersection(*column_sets))

len(common_columns)


# In[10]:


# Filter each DataFrame in selected_dfs to include only common columns
selected_dfs_filtered = [df.loc[:, common_columns] for df in selected_dfs]

# Concatenate the filtered dataframes along the rows
concatenated_df = pd.concat(selected_dfs_filtered, ignore_index=True)

# Save the concatenated dataframe to a file
output_concatenated_file = pathlib.Path(output_dir, "concatenated_norm_fs_plates_5_3_3prime_4controls.parquet")
concatenated_df.to_parquet(output_concatenated_file, index=False)

print(concatenated_df.shape)
concatenated_df.head()


# In[11]:


desired_columns = ["Metadata_Plate","Metadata_Well", "Metadata_Site", "Metadata_number_of_singlecells", "Metadata_genotype"]

# Make sure to reinitialize UMAP instance
umap_fit = umap.UMAP(
    random_state=umap_random_seed,
    n_components=umap_n_components
)

# Process cp_df to separate features and metadata
cp_features = infer_cp_features(concatenated_df)
meta_features = infer_cp_features(concatenated_df, metadata=True)
filtered_meta_features = [feature for feature in meta_features if feature in desired_columns]

# Fit UMAP and convert to pandas DataFrame
embeddings = pd.DataFrame(
    umap_fit.fit_transform(concatenated_df.loc[:, cp_features]),
    columns=[f"UMAP{x}" for x in range(0, umap_n_components)]
)
print(embeddings.shape)

# Combine with metadata
cp_umap_with_metadata_df = pd.concat([
    concatenated_df.loc[:, filtered_meta_features],
    embeddings
], axis=1)

# randomize the rows of the dataframe to plot the order of the data evenly
cp_umap_with_metadata_df = cp_umap_with_metadata_df.sample(frac=1, random_state=0)

# Generate output file and save
output_umap_file = pathlib.Path(output_dir, f"UMAP_concat_model_plates_sc_feature_selected.tsv")
cp_umap_with_metadata_df.to_csv(output_umap_file, index=False, sep="\t")

