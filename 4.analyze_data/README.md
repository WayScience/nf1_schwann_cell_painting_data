# Analyze NF1 data

In this module, we perform analysis on the data to uncover answers to our goals as specified in [the main README](../README.md).


The analyses we perform are:

1. Linear modeling per feature in each plate. The beta coefficients for WT treatment contribution and cell count contribution are plotted as a scatter plot.

# R visualization environment

To visualize results, we use R to create plots. 
This means that we have a separate environment from the main Python environment specifically in this module that has an R kernel.
To install this environment, perform the following steps:

```bash
# Make sure you are in the 4.analyze_data module to access the env file
cd 4.analyze_data
# Run this command in terminal to create the conda environment
conda env create -f r_analysis_env.yml
```
