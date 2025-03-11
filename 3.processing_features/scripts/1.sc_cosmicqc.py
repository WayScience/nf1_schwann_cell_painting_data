#!/usr/bin/env python
# coding: utf-8

# # Perform single-cell quality control
# 
# In this notebook, we perform single-cell quality control using [coSMicQC](https://github.com/WayScience/coSMicQC). 
# We filter the single cells by identifying outliers with z-scores, and use either combinations of features or one feature for each condition. For more information on the functions, please refer [**here**](https://github.com/WayScience/coSMicQC/blob/main/src/cosmicqc/analyze.py).
# 
# NOTE: As this method uses z-scoring, there is an automatic assumption that the distribution of the features are normal. If they are not, this method will be less likely to work. We have confirmed the features we are using are of normal distribution.
# 
# We use the feature(s) below to assess the technical quality of the segmented single-cells:
# 
# ### Assessing poor nuclei segmentation
# 
# To identify nuclei segmentations that include multiple nuclei, we use the following feature as one condition:
# 
# - **Nuclei Solidity:** This metric quantifies how irregularly shaped a nuclei segmentation is. A value of 1 indicates that the segmentation is perfectly round and lower values indicate a very irregularly shaped nuclei (e.g., lot of indentation or protrusions).
# 
# To identify nuclei segmentations where the respective nuclei is over-saturated, we use the following feature as another condition.
# 
# - **Nuclei Mean Intensity:** This metric quantifies the average intensity of all pixels in a nuclei segmentation. Higher values mean that the pixels tend to be more intense, resulting in a blow-out or over-saturated nuclei, which can sometimes because of the staining.

# ## Import libraries

# In[1]:


import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yaml

from cosmicqc import find_outliers


# ## Define helper function

# In[2]:


def reshape_data(df: pd.DataFrame, feature_col: str, feature_name: str) -> pd.DataFrame:
    """Reshape the data for generating plot for each quality control feature

    Args:
        df (pd.DataFrame): dataframe that will be reshaped for plotting
        feature_col (str): feature column with CP format to rename
        feature_name (str): renamed column

    Returns:
        pd.DataFrame: reshaped dataframe to use for plotting
    """
    return df[["Image_Metadata_Plate", "plate_alias", feature_col, "Dataset"]].rename(
        columns={feature_col: "Value"}
    ).assign(Feature=feature_name)


# ## Set paths and variables

# In[3]:


# Directory with data
data_dir = pathlib.Path("./data/converted_data/").resolve(strict=True)

# Directory to save cleaned data
cleaned_dir = pathlib.Path("./data/cleaned_profiles/")
cleaned_dir.mkdir(exist_ok=True)

# Directory to save qc figures
qc_fig_dir = pathlib.Path("./qc_figures")
qc_fig_dir.mkdir(exist_ok=True)

# metadata columns to include in output data frame
metadata_columns = [
    "Image_Metadata_Plate",
    "plate_alias",
    "Image_Metadata_Well",
    "Image_Metadata_Site",
    "Metadata_Nuclei_Location_Center_X",
    "Metadata_Nuclei_Location_Center_Y",
]

# Path to dictionary
dictionary_path = pathlib.Path("./plate_info_dictionary.yaml")


# ## Load in dictionary of plates to process

# In[4]:


# Load plate information from YAML file
with open(dictionary_path, "r") as file:
    plate_info = yaml.safe_load(file)

# Load in specific plates relevant to manuscript
plates = ["Plate_3_prime", "Plate_3", "Plate_5", "Plate_6"]

# Load in specified plates from plate_info_dictionary
plates = plate_info.keys()
dfs = {plate: pd.read_parquet(plate_info[plate]['dest_path']) for plate in plates}

# Concatenate all dataframes into a single dataframe
combined_df = pd.concat(dfs.values(), ignore_index=True)

# Create a mapping for plate aliases
plate_alias_mapping = {
    "Plate_3": "Plate A",
    "Plate_3_prime": "Plate B",
    "Plate_5": "Plate C",
    "Plate_6": "Plate D"
}

# Add the plate_alias column
combined_df['plate_alias'] = combined_df['Image_Metadata_Plate'].map(plate_alias_mapping)

# Print output
print(combined_df.shape)
combined_df.head()


# ## Over-saturated nuclei (mitosis/debris)
# 
# NOTE: Threshold was determined with trial and error to find where the cutoff for good to bad quality or mitosis-ing single-cells are.

# In[ ]:


# Set outlier threshold that maximizes removing most technical outliers and minimizes good cells
outlier_threshold = 2

# find nuclei with overly high intensity (over-saturated)
feature_thresholds = {
    "Nuclei_Intensity_MeanIntensity_DAPI": outlier_threshold,
}

nuclei_high_int_outliers = find_outliers(
    df=combined_df,
    metadata_columns=metadata_columns,
    feature_thresholds=feature_thresholds
)

# Sort the outliers by Nuclei_Intensity_MeanIntensity_DAPI
nuclei_high_int_outliers = nuclei_high_int_outliers.sort_values(by="Nuclei_Intensity_MeanIntensity_DAPI", ascending=True)

print(nuclei_high_int_outliers.shape)
nuclei_high_int_outliers.head()


# In[6]:


# Print out the number of outliers across plates
outlier_counts = nuclei_high_int_outliers['Image_Metadata_Plate'].value_counts()

# Calculate the percentage of outliers
total_counts = combined_df['Image_Metadata_Plate'].value_counts()
outlier_percentages = (outlier_counts / total_counts) * 100

# Print the counts and percentages
for plate, count in outlier_counts.items():
    print(f"{plate}: {count} outliers ({outlier_percentages[plate]:.2f}%)")


# ## Over-segmented nuclei (reflected by irregular, non-circular shape)
# 
# NOTE: Threshold was determined with trial and error to find where the cutoff for good to bad quality single-cell are.

# In[7]:


# Set outlier threshold that maximizes removing most technical outliers and minimizes good cells
outlier_threshold = -1.5

# find irregular shaped nuclei
feature_thresholds = {
    "Nuclei_AreaShape_Solidity": outlier_threshold,
}

irregular_nuclei_outliers = find_outliers(
    df=combined_df,
    metadata_columns=metadata_columns,
    feature_thresholds=feature_thresholds
)

print(irregular_nuclei_outliers.shape)
irregular_nuclei_outliers.sort_values(by="Nuclei_AreaShape_Solidity", ascending=True).head()


# In[8]:


# Print out the number of outliers across plates
outlier_counts = irregular_nuclei_outliers['Image_Metadata_Plate'].value_counts()

# Calculate the percentage of outliers
total_counts = combined_df['Image_Metadata_Plate'].value_counts()
outlier_percentages = (outlier_counts / total_counts) * 100

# Print the counts and percentages
for plate, count in outlier_counts.items():
    print(f"{plate}: {count} outliers ({outlier_percentages[plate]:.2f}%)")


# In[9]:


# Remove outliers from combined_df
outlier_indices = nuclei_high_int_outliers.index.union(irregular_nuclei_outliers.index)
filtered_combined_df = combined_df.drop(outlier_indices)
print(filtered_combined_df.shape[0])


# ## Generate plot

# In[10]:


# Set palette for plot
palette = {
    "Passing single-cells": "darkgreen",
    "High intensity nuclei\nfailed single-cells": "magenta",
    "Irregular shape\nfailed single-cells": "magenta",
}

# Add dataset labels
for df, label in [
    (filtered_combined_df, "Passing single-cells"),
    (nuclei_high_int_outliers, "High intensity nuclei\nfailed single-cells"),
    (irregular_nuclei_outliers, "Irregular shape\nfailed single-cells"),
]:
    df["Dataset"] = label

plot_df = pd.concat([
    reshape_data(filtered_combined_df, "Nuclei_Intensity_MeanIntensity_DAPI", "Nuclei Intensity (Mean DAPI)"),
    reshape_data(nuclei_high_int_outliers, "Nuclei_Intensity_MeanIntensity_DAPI", "Nuclei Intensity (Mean DAPI)"),
    reshape_data(irregular_nuclei_outliers, "Nuclei_AreaShape_Solidity", "Nuclei AreaShape (Solidity)"),
    reshape_data(filtered_combined_df, "Nuclei_AreaShape_Solidity", "Nuclei AreaShape (Solidity)"),
])

# Create FacetGrid with 2x2 layout per feature
for feature in plot_df["Feature"].unique():
    feature_df = plot_df[plot_df["Feature"] == feature]  # Subset data

    g = sns.FacetGrid(
        feature_df,
        col="plate_alias",
        hue="Dataset",
        palette=palette,
        height=4,
        aspect=1.5,
        sharex=True,
        sharey=False,
        col_wrap=2  # Ensures 2x2 layout
    )

    # Plot histograms with dodged bars
    g.map(sns.histplot, "Value", bins=40, binrange=(0, 1), alpha=0.7, edgecolor="black", multiple="dodge")

    # Customize labels and titles
    g.set_xlabels("Feature value (range 0-1)", fontsize=14)
    g.set_ylabels("Single-cell count", fontsize=14)
    g.set_titles(col_template="{col_name}", size=16)
    # Adjust tick labels size
    for ax in g.axes.flat:
        ax.tick_params(labelsize=14)

    # Add the legend
    g.add_legend(title="Dataset", bbox_to_anchor=(1.05, 0.5), loc="center left", prop={"size": 14})

    # Retrieve the legend object
    legend = g._legend  # Access the legend from the FacetGrid

    # Adjust the legend title font size
    legend.set_title("Dataset")
    legend.get_title().set_fontsize(14)


    # Add a suptitle for the feature
    g.figure.suptitle(feature, fontsize=18, fontweight="bold")
    g.figure.subplots_adjust(top=0.85)  # Adjust spacing for title

    if feature == "Nuclei Intensity (Mean DAPI)":
        feature = "nuclei_int_dapi"
    else:
        feature = "nuclei_solidity"

    plt.tight_layout()
    g.savefig(f"{qc_fig_dir}/cosmicqc_distribution_{feature}.png", dpi=500)


# In[11]:


# Collect the indices of the outliers
outlier_indices = pd.concat([nuclei_high_int_outliers, irregular_nuclei_outliers]).index

# Remove rows with outlier indices from combined_df
combined_df_cleaned = combined_df.drop(outlier_indices)

# Save cleaned data for each plate and update the dictionary with cleaned paths
for plate in plates:
    plate_df_cleaned = combined_df_cleaned[combined_df_cleaned['Image_Metadata_Plate'] == plate]
    plate_df_cleaned = plate_df_cleaned.drop(columns=['plate_alias'])  # Remove plate_alias column
    cleaned_path = f"{cleaned_dir}/{plate}_cleaned.parquet"
    plate_df_cleaned.to_parquet(cleaned_path)
    plate_info[plate]['cleaned_path'] = cleaned_path
    print(plate, ":", plate_df_cleaned.shape)

# Print the number of outliers removed and percentage from the total per plate
for plate in plates:
    original_count = total_counts[plate]
    outlier_count = outlier_counts.get(plate, 0)
    percentage_removed = outlier_percentages.get(plate, 0)
    print(f"{plate}: {outlier_count} outliers removed ({percentage_removed:.2f}%) from {original_count} total cells")


# ## Dump the new cleaned path to the dictionary for downstream processing

# In[12]:


with open(dictionary_path, "w") as file:
    yaml.dump(plate_info, file)

