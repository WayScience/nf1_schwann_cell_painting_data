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

## CellProfiler Parallel

To improve the speed for analysis, we have implemented `CellProfiler Parallel`, which utilizes multi-processing to run one plate per CPU core.

### Speed when running CellProfiler Parallel

When using CellProfiler Parallel to run analysis on 5 plates, it took approximately 28 hours to finish on a Linux-based machine running Pop_OS! LTS 22.04 with an AMD Ryzen 7 3700X 8-Core Processor with 16 CPU workers.

### Speed when running CellProfiler Sequential

To run analysis on plates 1 and 2, it took approximately one hour. 
To run analysis on plates 3 and 3 prime, it took approximately 31 hours (~ 16 hours each).
The analysis was run on a Linux-based machine running Pop_OS! LTS 22.04 with an AMD Ryzen 7 3700X 8-Core Processor.

#### Difference in speed

When looking at the log files, a fifth plate (e.g., `Plate_4``) took about **24 hours** to processes. 
Added on to the CellProfiler Sequential, which in total took 32 hours for 4 plates, it would likely have added on another 10-14 hours (given how long plates 3 and 3 prime took), totalling **over 45 hours**.

Even though plates individually ran faster, the computational time saved by running them in parallel **saves over 20 hours of time**. 

What might be able to improve the individual processing time per plate could be to increase the number of workers (even though CellProfiler CLI should only be using one core per processes). 
Currently, CellProfiler Parallel will automatically set the number of workers based on the number of commands (e.g., plates to be processed).
Depending on needs, a parameter can be added to manually set the max_workers.

## Accessing the CellProfiler output - SQLite files

We used Git LFS to store the large files like SQLite files.
If you would like to access these files after cloning the repo, you will need to run the below command in terminal. 

**Note:** Make sure that you have Git LFS installed on your local machine. Follow the instructions on [the GitHub Docs](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage).

```bash
git lfs pull
```

