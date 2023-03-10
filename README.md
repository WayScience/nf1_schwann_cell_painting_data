# NF1 Cell Painting Data 

## Data

The data we use is a modified Cell Painting assay on [Schwann cells](https://www.ncbi.nlm.nih.gov/books/NBK544316/) from patients with [Neurofibromatosis type 1 (NF1)](https://medlineplus.gov/genetics/condition/neurofibromatosis-type-1/). 
In this modified Cell Painting, there are three channels for plates 1 and 2:

- `DAPI` (Nuclei)
- `GFP` (Endoplasmic Reticulum)
- `RFP` (Actin)

![Modified_Cell_Painting.png](example_figures/Modified_Cell_Painting.png)

Plates 1 and 2 measure Cell Painting in isogenic Schwann cells with two different NF1 genotypes:

**Plate 1**
- Wild type (`WT +/+`): In column 6 from the plate (e.g C6, D6, etc.)
- Null (`Null -/-`): In column 7 from the plate (e.g C7, D7, etc.)
There are only rows C-F in this plate.

**Plate 2**
- Wild type (`WT +/+`): Columns 1 and 6
- Null (`Null -/-`): Columns 7 and 12
This plate uses all rows (e.g., A-H)

It is important to study Schwann cells from NF1 patients because NF1 causes patients to develop neurofibromas, which are red bumps on the skin (tumors) that appear due to the loss of Ras-GAP neurofibromin. 
This loss occurs when the NF1 gene is mutated (NF1 +/-).

## Goal

The goal of this project is to predict NF1 genotype from Schwann cell morphology. 
We apply cell image analysis to Cell Painting images and use representation learning to extract morphology features.
We will apply machine learning to the morphology features to discover a biomarker of NF1 genotype.
Once we discover a biomarker from these cells, we hope that our method can be used for drug discovery to treat this rare disease.

## Repository Structure

| Module | Purpose | Description |
| :---- | :----- | :---------- |
| [0_download_data](0_download_data/) | Download NF1 pilot data | Download images from each plate of NF1 dataset for analysis from Figshare |

## Main environment

For all modules, we use one main environment for the repository, which includes all packages needed including installing CellProfiler v4.2.4.

To create the environment, run the below code block:

```bash
# Run this command in terminal to create the conda environment
conda env create -f nf1_cellpainting_env.yml
```

Make sure that the conda environment is activated before running notebooks or scripts:

```bash
conda activate nf1_cellpainting_data
```
