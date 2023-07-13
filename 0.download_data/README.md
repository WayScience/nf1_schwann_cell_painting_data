# Download images from each plate from the NF1 Schwann cell project

In this module, we download the images and platemap metadata for each plate from [Figshare](https://figshare.com/), which is a open-source repository that holds data/figures/etc. to preserve and share. 
The plates for this project are located at [NF1 Schwann Cell Genotype Cell Painting Assay](https://figshare.com/projects/NF1_Schwann_Cell_Genotype_Cell_Painting_Assay/161620) on Figshare.

## Run the `download_plates` notebook

**Note:** Confirm that the shell name in the cp_analysis.sh file is correct for your machine (e.g. Linux = bash, MacOS = zsh).

To download the images for each plate and separate the metadata from the images, run the [download_plates.ipynb](download_plates.ipynb) notebook as a python script using the code block below:

```bash
# Run this script in terminal
cd 0.download_data
source download_plates.sh
```

To download 4 plates from figshare, it took about 50 minutes. 
There is the option to parallelize this in the future depending on needs.
