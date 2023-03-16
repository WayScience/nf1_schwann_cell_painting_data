# Perform illumination correction and save corrected images

In this module, we perform illumination correction (IC) on images for each plate and save the corrected images into new folders. 
Images are saved as 16-bit depth, which is the same as the raw data.

## Run the `nf1_ic` notebook

To calculate and apply an IC function on each channel, run the [nf1_ic.ipynb](nf1_ic.ipynb) notebook as a python script using the code block below:

```bash
# Run this script in terminal
# move to the 1.cellprofiler_ic directory to acess the `sh` script
cd 1.cellprofiler_ic
# run the notebook as a python script
bash nf1_ic.sh
```
