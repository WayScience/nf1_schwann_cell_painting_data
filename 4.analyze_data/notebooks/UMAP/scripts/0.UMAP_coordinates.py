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
        cp_df.loc[:, filtered_meta_features],
        embeddings
    ], axis=1)
    
    # randomize the rows of the dataframe to plot the order of the data evenly
    cp_umap_with_metadata_df = cp_umap_with_metadata_df.sample(frac=1, random_state=0)

    # Generate output file and save
    output_umap_file = pathlib.Path(output_dir, f"UMAP_{plate_name}.tsv")
    cp_umap_with_metadata_df.to_csv(output_umap_file, index=False, sep="\t")


# In[6]:


# Print an example output file
cp_umap_with_metadata_df.head()


# In[7]:


# Set constants
feature_select_ops = [
    "variance_threshold",
    "correlation_threshold",
    "blocklist",
    "drop_na_columns"
]

# Set input paths
data_dir = pathlib.Path("../../../3.processing_features/data/single_cell_profiles/")

# Select only the feature selected files
norm_suffix = "*sc_normalized.parquet"

# Obtain file paths for all feature selected plates
norm_files = glob.glob(f"{data_dir}/{norm_suffix}")
norm_files


# In[8]:


# Select file paths for plates 5, 3, and 3 prime only
selected_plates = ["Plate_5", "Plate_3", "Plate_3_prime"]

# Filter and concatenate the selected plates
selected_dfs = []
for file_path in norm_files:
    plate_name = pathlib.Path(file_path).stem.replace("_sc_normalized", "")

    # Only read in selected plates
    if plate_name in selected_plates:
        df = pd.read_parquet(file_path)

        # Update Metadata_Plate for Plate_3_prime
        if plate_name == "Plate_3_prime":
            df["Metadata_Plate"] = "Plate_3_prime"

        selected_dfs.append(df)

# Concatenate the dataframes along the rows
concatenated_df = pd.concat(selected_dfs, ignore_index=True)

# perform feature selection with all plates concat
concat_cp_df = feature_select(
        concatenated_df,
        operation=feature_select_ops,
        na_cutoff=0
    )

# Save the concatenated dataframe to a file
output_concatenated_file = pathlib.Path(output_dir, "concatenated_norm_fs_plates_5_3_3prime.parquet")
concatenated_df.to_parquet(output_concatenated_file, index=False)

print(concat_cp_df.shape)
concat_cp_df


# In[9]:


desired_columns = ["Metadata_Plate","Metadata_Well", "Metadata_Site", "Metadata_number_of_singlecells", "Metadata_genotype"]

# Make sure to reinitialize UMAP instance
umap_fit = umap.UMAP(
    random_state=umap_random_seed,
    n_components=umap_n_components
)

# Process cp_df to separate features and metadata
cp_features = infer_cp_features(concat_cp_df)
meta_features = infer_cp_features(concat_cp_df, metadata=True)
filtered_meta_features = [feature for feature in meta_features if feature in desired_columns]

# Fit UMAP and convert to pandas DataFrame
embeddings = pd.DataFrame(
    umap_fit.fit_transform(concat_cp_df.loc[:, cp_features]),
    columns=[f"UMAP{x}" for x in range(0, umap_n_components)]
)
print(embeddings.shape)

# Combine with metadata
cp_umap_with_metadata_df = pd.concat([
    concat_cp_df.loc[:, filtered_meta_features],
    embeddings
], axis=1)

# randomize the rows of the dataframe to plot the order of the data evenly
cp_umap_with_metadata_df = cp_umap_with_metadata_df.sample(frac=1, random_state=0)

# Generate output file and save
output_umap_file = pathlib.Path(output_dir, f"UMAP_Concat_sc_feature_selected.tsv")
cp_umap_with_metadata_df.to_csv(output_umap_file, index=False, sep="\t")

