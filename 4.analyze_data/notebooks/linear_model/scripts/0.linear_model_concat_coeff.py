#!/usr/bin/env python
# coding: utf-8

# # Perform linear model per CellProfiler feature on concatenated normalized data from plates 5, 3 prime, and 3
# 
# We will include 3 co-variates:
# 
# 1. Cell count per well contribution
# 2. Plate contribution
# 3. Genotype contribution (WT versus Null)

# In[1]:


import pathlib

import pandas as pd
from pycytominer import feature_select
from pycytominer.cyto_utils import infer_cp_features
from sklearn.linear_model import LinearRegression


# In[2]:


# Define inputs and outputs
data_dir = pathlib.Path("../../../3.processing_features/data/single_cell_profiles/")
cp_files = [
    pathlib.Path(data_dir, f"Plate_{plate}_sc_normalized.parquet")
    for plate in ["5", "3", "3_prime"]
]

# Output directory for LM coeffs
output_dir = pathlib.Path("./results")
output_dir.mkdir(exist_ok=True)

# Name of output file with LM coeffs
output_cp_file = pathlib.Path(
    output_dir, "linear_model_cp_features_concat_plate5_plate3_plate3prime.tsv"
)

# Filter and load the specified files
df_list = []

for plate in cp_files:
    cp_file = pathlib.Path(plate)

    if cp_file.exists():
        # Load the parquet file into a DataFrame without HET rows
        df = pd.read_parquet(cp_file, filters=[('Metadata_genotype', '!=', 'HET')])

        # Update Metadata_Plate only for Plate_3_prime since during CellProfiler analysis, the metadata only caught Plate_3
        if plate.stem.replace("_sc_normalized", "") == "Plate_3_prime":
            df["Metadata_Plate"] = "Plate_3_prime"

        df_list.append(df)

# Concatenate the DataFrames
concat_df = pd.concat(df_list, ignore_index=True)

# Make sure there are no NaNs
concat_df = feature_select(concat_df, operation="drop_na_columns", na_cutoff=0)

# Define CellProfiler features
cp_features = infer_cp_features(concat_df)

print(f"We are testing {len(cp_features)} CellProfiler features")
print(concat_df.shape)
concat_df.head()


# ## Set up binary framework for WT versus Null and plate to plate comparison

# In[3]:


# Setup linear modeling framework
variables = ["Metadata_number_of_singlecells"]
X = concat_df.loc[:, variables]

# Add binary matrix of categorical genotypes
genotype_x = pd.get_dummies(data=concat_df.Metadata_genotype)

# Add binary matrix of categorical plates
plate_x = pd.get_dummies(data=concat_df.Metadata_Plate)

X = pd.concat([X, genotype_x, plate_x], axis=1)

print(X.shape)
X.head()


# In[4]:


# Fit linear model for each feature
lm_results = []
for cp_feature in cp_features:
    # Subset CP data to each individual feature (univariate test)
    cp_subset_df = concat_df.loc[:, cp_feature]

    # Fit linear model
    lm = LinearRegression(fit_intercept=True)
    lm_result = lm.fit(X=X, y=cp_subset_df)

    # Extract Beta coefficients
    # (contribution of feature to X covariates)
    coef = lm_result.coef_

    # Estimate fit (R^2)
    r2_score = lm.score(X=X, y=cp_subset_df)

    # Add results to a growing list
    lm_results.append([cp_feature, r2_score] + list(coef))


# In[5]:


# Convert results to a pandas DataFrame
lm_results = pd.DataFrame(
    lm_results,
    columns=[
        "feature",
        "r2_score",
        "cell_count_coef",
        "Null_coef",
        "WT_coef",
        "Plate_3_coef",
        "Plate_3_prime_coef",
        "Plate_5_coef",
    ],
)

# Output file
lm_results.to_csv(output_cp_file, sep="\t", index=False)

print(lm_results.shape)
lm_results.head()

