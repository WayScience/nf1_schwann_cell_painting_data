# Segmentation and feature extraction using CellProfiler

In this module, we segment nuclei, cytoplasms, and whole cells from images and perform feature extraction using CellProfiler.

## Run the `nf1_analysis` notebook

To run the CellProfiler analysis pipeline on the illumination corrected images for each plate, run the [nf1_analysis.ipynb](nf1_analysis.ipynb) notebook as a python script using the code block below:

**Note:** Confirm that the shell name in the [nf1_analysis.sh](nf1_analysis.sh) file is correct for your machine (e.g. Linux = `bash`, MacOS = `zsh`)

```bash
# Run this script in terminal
# move to the 2.cellprofiler_analysis directory to access the `sh` script
cd 2.cellprofiler_analysis
# run the notebook as a python script
source nf1_analysis.sh
```

To run analysis on plates 1 and 2, it took approximately one hour. 
To run analysis on plates 3 and 3 prime, it took approximately 31 hours.
The analysis was run on a Linux-based machine running Pop_OS! LTS 22.04 with an AMD Ryzen 7 3700X 8-Core Processor.

## Accessing the CellProfiler output - SQLite files

We used Git LFS to store the large files like SQLite files.
If you would like to access these files after cloning the repo, you will need to run the below command in terminal. 

**Note:** Make sure that you have Git LFS installed on your local machine. Follow the instructions on [the GitHub Docs](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage).

```bash
git lfs pull
```

