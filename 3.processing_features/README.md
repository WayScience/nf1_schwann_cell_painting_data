# Extract single cells from CellProfiler output + normalize and feature select

In this module, we extract single cell data from the CellProfiler .sqlite file outputs, convert to parquet files, and perform annotation to add platemap metadata, normalize features, and perform feature selection on the normalized features.

## CytoTable

We use [CytoTable](https://github.com/cytomining/CytoTable/tree/main) to extract single cells and merge them from the SQLite outputs and convert into paraquet files.

**NOTE:** There is currently a bug where extra rows of all `NaNs` are being added into the converted files. In the notebook, we rewrite the file to remove those artifacts. This issue is noted in the CytoTable repo here: https://github.com/cytomining/CytoTable/issues/86

## Pycytominer

We use [Pycytominer](https://github.com/cytomining/pycytominer) to perform the annotation, normalization, and feature selection of the merged single cell data (parquet files from CytoTable).

For more information regarding the functions that we used, please see [the documentation](https://pycytominer.readthedocs.io/en/latest/) from the Pycytominer team.

## Extract and process single cell features from CellProfiler

Using the code below, execute the `sh` file and merge single cells to use for annotation, normalization, and feature selection.

**Note:** To prevent kernel issues, the processes is split into separate notebooks (one for each step). 

```bash
# cd to directory with sh file
cd 3.processing_features
source processing_features.sh
```

## Accessing the CellProfiler output - Parquet files

We used Git LFS to store the large files like Parquet files.
If you would like to access these files after cloning the repo, you will need to run the below command in terminal. 

**Note:** Make sure that you have Git LFS installed on your local machine. Follow the instructions on [the GitHub Docs](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage).

```bash
git lfs pull
```
