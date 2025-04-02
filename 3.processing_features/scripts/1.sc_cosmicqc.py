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
# To identify nuclei segmentations that include multiple nuclei, we use the following feature(s) as one condition:
# 
# - **Nuclei Solidity:** This metric quantifies how irregularly shaped a nuclei segmentation is. A value of 1 indicates that the segmentation is perfectly round and lower values indicate a very irregularly shaped nuclei (e.g., lot of indentation or protrusions).
# - **Nuclei Integrated Intensity:** This metric quantifies the total intensity of all pixels in a nuclei segmentation. Higher values mean that there are likely more pixels which can indicate multiple nuclei within the segmentation.
# 
# To identify nuclei segmentations where the respective nuclei is over-saturated or undergoing mitosis, we use the following feature(s) as two more conditions.
# 
# - **Nuclei Upper Quartile Intensity:** This metric quantifies the distribution of the pixel intensities in which 75% of pixels fall below the value (capturing the top 25% of pixel intensities). Values near 1 from this metric indicate that most pixel intensities are at a very high value.
# - **Nuclei MAD (Median Absolute Deviation) Intensity:** This metric quantifies the variability of pixel intensities within the nuclei. Higher values of this metric indicate more texture while very low values indicate very little differences between pixel intensities (e.g., low variance).

# ## Import libraries

# In[1]:


import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yaml

from cosmicqc import find_outliers
from cytodataframe import CytoDataFrame


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
    return (
        df[["Image_Metadata_Plate", "plate_alias", feature_col, "Dataset"]]
        .rename(columns={feature_col: "Value"})
        .assign(Feature=feature_name)
    )


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
    "Image_FileName_DAPI",
    "Image_PathName_DAPI",
    "Nuclei_AreaShape_BoundingBoxMaximum_X",
    "Nuclei_AreaShape_BoundingBoxMaximum_Y",
    "Nuclei_AreaShape_BoundingBoxMinimum_X",
    "Nuclei_AreaShape_BoundingBoxMinimum_Y",
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
dfs = {plate: pd.read_parquet(plate_info[plate]["dest_path"]) for plate in plates}

# Concatenate all dataframes into a single dataframe
combined_df = pd.concat(dfs.values(), ignore_index=True)

# Create a mapping for plate aliases
plate_alias_mapping = {
    "Plate_3": "Plate A",
    "Plate_3_prime": "Plate B",
    "Plate_5": "Plate C",
    "Plate_6": "Plate D",
}

# Add the plate_alias column
combined_df["plate_alias"] = combined_df["Image_Metadata_Plate"].map(
    plate_alias_mapping
)

# Print output
print(combined_df.shape)
combined_df.head()


# In[5]:


from PIL import Image

def do_not_adjust_image_brightness(image: Image.Image) -> Image.Image:
    """
    Does nothing to the image and returns it unchanged.

    Args:
        image (Image.Image): The input PIL Image.

    Returns:
        Image.Image: The unchanged PIL Image.
    """
    # Return the input image as is without any modifications
    return image


# In[6]:


# Define the QC features
qc_features = [
    "Nuclei_Intensity_UpperQuartileIntensity_DAPI",
    "Nuclei_Intensity_IntegratedIntensity_DAPI",
    "Nuclei_Intensity_MADIntensity_DAPI",
    "Nuclei_AreaShape_Solidity",
]

# Filter combined_df to only include metadata columns and QC features
filtered_combined_df = combined_df[metadata_columns + qc_features]

filtered_combined_df_cdf = CytoDataFrame(
    data=filtered_combined_df,
    image_adjustment=do_not_adjust_image_brightness
)[
    [
        "Image_FileName_DAPI",
        "Nuclei_Intensity_MADIntensity_DAPI",
        "Nuclei_AreaShape_Solidity",
        "Nuclei_Intensity_UpperQuartileIntensity_DAPI"
    ]
]

# Sample 2 rows from the dataframe
filtered_combined_df_cdf.sample(n=2, random_state=0)


# ## Over-saturated nuclei (mitosis/debris)
# 
# NOTE: Threshold was determined with trial and error to find where the cutoff for good to bad quality or mitosis-ing single-cells are.

# In[7]:


# Set outlier threshold that maximizes removing most technical outliers and minimizes good cells
outlier_threshold = 1.0

# find nuclei with overly high intensity (over-saturated)
feature_thresholds = {
    "Nuclei_Intensity_UpperQuartileIntensity_DAPI": 2,
}

nuclei_high_int_outliers = find_outliers(
    df=filtered_combined_df,
    metadata_columns=metadata_columns,
    feature_thresholds=feature_thresholds,
)

nuclei_high_int_outliers_cdf = CytoDataFrame(
    data=nuclei_high_int_outliers,
    image_adjustment=do_not_adjust_image_brightness
)[
    [
        "Nuclei_Intensity_UpperQuartileIntensity_DAPI",
        "Image_FileName_DAPI",
    
    ]
]

# Sort the outliers
nuclei_high_int_outliers_cdf = nuclei_high_int_outliers_cdf.sort_values(
    by="Nuclei_Intensity_UpperQuartileIntensity_DAPI", ascending=True
)

print(nuclei_high_int_outliers_cdf.shape)
nuclei_high_int_outliers_cdf.head(2)


# In[8]:


nuclei_high_int_outliers_cdf.sample(n=5, random_state=0)


# In[9]:


# Print out the number of outliers across plates
outlier_counts = nuclei_high_int_outliers["Image_Metadata_Plate"].value_counts()

# Calculate the percentage of outliers
total_counts = combined_df["Image_Metadata_Plate"].value_counts()
outlier_percentages = (outlier_counts / total_counts) * 100

# Print the counts and percentages
for plate, count in outlier_counts.items():
    print(f"{plate}: {count} outliers ({outlier_percentages[plate]:.2f}%)")


# In[10]:


# Set outlier threshold that maximizes removing most technical outliers and minimizes good cells
outlier_threshold = 1.0

# find nuclei with overly high intensity (over-saturated)
feature_thresholds = {
    "Nuclei_Intensity_MADIntensity_DAPI": 2,
}

blurry_nuclei_outliers = find_outliers(
    df=filtered_combined_df,
    metadata_columns=metadata_columns,
    feature_thresholds=feature_thresholds,
)

blurry_nuclei_outliers_cdf = CytoDataFrame(
    data=blurry_nuclei_outliers,
    image_adjustment=do_not_adjust_image_brightness
)[
    [
        "Nuclei_Intensity_MADIntensity_DAPI",
        "Image_FileName_DAPI",
    
    ]
]

# Sort the outliers
blurry_nuclei_outliers_cdf = blurry_nuclei_outliers_cdf.sort_values(
    by="Nuclei_Intensity_MADIntensity_DAPI", ascending=True
)

print(blurry_nuclei_outliers_cdf.shape)
blurry_nuclei_outliers_cdf.head(2)


# In[11]:


blurry_nuclei_outliers_cdf.sample(n=5, random_state=0)


# In[12]:


# Print out the number of outliers across plates
outlier_counts = blurry_nuclei_outliers["Image_Metadata_Plate"].value_counts()

# Calculate the percentage of outliers
total_counts = combined_df["Image_Metadata_Plate"].value_counts()
outlier_percentages = (outlier_counts / total_counts) * 100

# Print the counts and percentages
for plate, count in outlier_counts.items():
    print(f"{plate}: {count} outliers ({outlier_percentages[plate]:.2f}%)")


# ## Over-segmented nuclei (reflected by irregular, non-circular shape)
# 
# NOTE: Threshold was determined with trial and error to find where the cutoff for good to bad quality single-cell are.

# In[13]:


# Set outlier threshold that maximizes removing most technical outliers and minimizes good cells
outlier_threshold = -2

# find irregular shaped nuclei
feature_thresholds = {
    "Nuclei_AreaShape_Solidity": -1.25,
    "Nuclei_Intensity_IntegratedIntensity_DAPI": 2
}

irregular_nuclei_outliers = find_outliers(
    df=filtered_combined_df,
    metadata_columns=metadata_columns,
    feature_thresholds=feature_thresholds,
)

irregular_nuclei_outliers_cdf = CytoDataFrame(
    data=irregular_nuclei_outliers,
    image_adjustment=do_not_adjust_image_brightness
)[
    [
        "Nuclei_AreaShape_Solidity",
        "Nuclei_Intensity_IntegratedIntensity_DAPI",
        "Image_FileName_DAPI",
    
    ]
]

print(irregular_nuclei_outliers_cdf.shape)
irregular_nuclei_outliers_cdf.sort_values(
    by="Nuclei_AreaShape_Solidity", ascending=False
).head(2)


# In[14]:


irregular_nuclei_outliers_cdf.sample(n=5, random_state=0)


# In[15]:


# Print out the number of outliers across plates
outlier_counts = irregular_nuclei_outliers["Image_Metadata_Plate"].value_counts()

# Calculate the percentage of outliers
total_counts = combined_df["Image_Metadata_Plate"].value_counts()
outlier_percentages = (outlier_counts / total_counts) * 100

# Print the counts and percentages
for plate, count in outlier_counts.items():
    print(f"{plate}: {count} outliers ({outlier_percentages[plate]:.2f}%)")


# In[16]:


# Remove outliers from combined_df
outlier_indices = (
    nuclei_high_int_outliers.index
    .union(irregular_nuclei_outliers.index)
    .union(blurry_nuclei_outliers.index)
)
dropped_outliers_combined_df = combined_df.drop(outlier_indices)
print(dropped_outliers_combined_df.shape[0])


# In[17]:


# Collect the indices of the outliers
outlier_indices = pd.concat([nuclei_high_int_outliers, irregular_nuclei_outliers, blurry_nuclei_outliers]).index

# Remove rows with outlier indices from combined_df
combined_df_cleaned = combined_df.drop(outlier_indices)

# Save cleaned data for each plate and update the dictionary with cleaned paths
for plate in plates:
    plate_df = combined_df[combined_df["Image_Metadata_Plate"] == plate]  # Original plate data
    plate_df_cleaned = combined_df_cleaned[combined_df_cleaned["Image_Metadata_Plate"] == plate]  # Cleaned plate data
    
    # Calculate number of failed cells (rows removed)
    failed_cells = plate_df.shape[0] - plate_df_cleaned.shape[0]
    
    # Calculate percentage of failed cells
    failed_percentage = (failed_cells / plate_df.shape[0]) * 100
    
    # Print the number of failed cells and the percentage
    print(f"{plate}: {failed_cells} cells failed ({failed_percentage:.2f}% failed)")

    # Clean the plate data
    plate_df_cleaned = plate_df_cleaned.drop(columns=["plate_alias"])  # Remove plate_alias column
    
    # Save cleaned data for each plate
    cleaned_path = f"{cleaned_dir}/{plate}_cleaned.parquet"
    plate_df_cleaned.to_parquet(cleaned_path)
    plate_info[plate]["cleaned_path"] = cleaned_path
    print(plate, ":", plate_df_cleaned.shape)


# ## Dump the new cleaned path to the dictionary for downstream processing

# In[18]:


with open(dictionary_path, "w") as file:
    yaml.dump(plate_info, file)

