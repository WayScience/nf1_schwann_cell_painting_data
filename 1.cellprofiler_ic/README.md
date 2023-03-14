## Perform illumination correction and save corrected images

In this module, we perform illumination correction (IC) on the images for each plate and save the corrected images into new folders. 
The images are saved as 16-bit depth, which is the same as the raw data.

## Run the `nf1_ic` notebook

To calculate and apply an IC function on each channel, run the [nf1_ic.ipynb](dnf1_ic.ipynb) notebook as a python script using the code block below:

```bash
# Run this script in terminal
conda activate nf1_cellpainting_data
cd 0.cellprofiler_ic
bash nf1_ic.sh
```
