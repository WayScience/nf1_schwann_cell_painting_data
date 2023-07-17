# Perform illumination correction and save corrected images

In this module, we perform illumination correction (IC) on images for each plate and save the corrected images into new folders. 
Images are saved as 16-bit depth, which is the same as the raw data.

## CellProfiler Pipeline

Due to there being differences in channel number between plates, we have two different illumination correction pipelines.

1. [3 channel pipeline](./NF1_illum_3channel.cppipe) -> This pipeline is used only with Plates 1 and 2 since these first pilot plates only had 3 channels.
2. [4 channel pipeline](./NF1_illum_4channel.cppipe) -> This pipeline is used for all the rest of the plates (and future plates) as we have established the protocol for staining. 

**Note:** The parameters for correction between pipelines in the same channel might be slightly different. 
But, the parameters in both perform and output the best corrected images at this point

## Run the `nf1_ic` notebook

To calculate and apply an IC function on each channel, run the [nf1_ic.ipynb](nf1_ic.ipynb) notebook as a python script using the code block below:

```bash
# Run this script in terminal
# move to the 1.cellprofiler_ic directory to access the `sh` script
cd 1.cellprofiler_ic
# run the notebook as a python script
source nf1_ic.sh
```

## CellProfiler Parallel

To improve the speed for correcting the images, we have implemented `CellProfiler Parallel`, which utilizes multi-processing to run one plate per CPU core.

### Speed when running CellProfiler Parallel

To run **five plates** through illumination correction, it took approximately **1 hour** in total on a computer using Pop_OS! 22.04 LTS with an AMD Ryzen 7 3700X 8-Core Processor.

This means that we are saving 2 hours (assuming the fifth plate running sequentially would take another hour totalling 3 hours) when running five plates.

### Speed when running CellProfiler sequentially

In the past, we ran one command per plate in seqential order (e.g., one plate is ran and once it finishes the next plate starts).

For four plates, it took about 2 hours to calculate, apply, and save illumination corrected images on a computer using Pop_OS! 22.04 LTS with an AMD Ryzen 7 3700X 8-Core Processor.

For three plates, it took about 18 hours to calculate and save illumination corrected images on a computer using MacOS Ventura 13.2.1 with the M2 chip.
