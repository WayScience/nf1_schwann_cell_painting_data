#!/usr/bin/env python
# coding: utf-8

# # Perform linear model per CellProfiler feature
# 

# ## Import libraries
# 

# In[1]:


import pathlib
import pandas as pd

from sklearn.linear_model import LinearRegression

from pycytominer.cyto_utils import infer_cp_features


# ## Set up paths and variables
# 

# In[2]:


# Define inputs and outputs
data_dir = pathlib.Path("../3.processing_features/data/single_cell_profiles/")
cp_file = pathlib.Path(data_dir, "Plate_4_sc_normalized.parquet")

output_dir = pathlib.Path("./results")
output_dir.mkdir(exist_ok=True)
output_cp_file = pathlib.Path(output_dir, "linear_model_cp_features_plate4.tsv")


# ## Read in normalized data
# 

# In[3]:


# Load data
cp_df = pd.read_parquet(cp_file)

# Remove rows where Metadata_genotype is "HET" to avoid using in the LM
cp_df = cp_df[cp_df["Metadata_genotype"] != "HET"]

# Define CellProfiler features
cp_features = infer_cp_features(cp_df)

print(f"We are testing {len(cp_features)} CellProfiler features")
print(cp_df.shape)
cp_df.head()


# ## Set up the dummy matrix between null and WT cell types
# 

# In[4]:


# Setup linear modeling framework
variables = ["Metadata_number_of_singlecells"]
X = cp_df.loc[:, variables]

# Add dummy matrix of categorical genotypes, excluding "HET"
genotype_x = pd.get_dummies(data=cp_df.Metadata_genotype)

X = pd.concat([X, genotype_x], axis=1)

print(X.shape)
X.head()


# ## Perform linear modeling per feature
# 

# In[5]:


# Fit linear model for each feature
lm_results = []
for cp_feature in cp_features:
    # Subset CP data to each individual feature (univariate test)
    cp_subset_df = cp_df.loc[:, cp_feature]

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

# Convert results to a pandas DataFrame
lm_results = pd.DataFrame(
    lm_results,
    columns=["feature", "r2_score", "cell_count_coef", "Null_coef", "WT_coef"],
)

# Output file
lm_results.to_csv(output_cp_file, sep="\t", index=False)

print(lm_results.shape)
lm_results.head()


# ## Check to make sure the processing worked
# 

# In[6]:


# Small exploration visualization
lm_results.plot(x="cell_count_coef", y="WT_coef", kind="scatter")


# In[ ]:




