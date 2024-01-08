#!/usr/bin/env python
# coding: utf-8

# # Rename SQLite files from each plate folder to include plate as the prefix
# 
# Due to the name of the SQLite file being hardcoded into the pipeline, the work-around when using `CellProfiler Parallel` is to output the SQLite files into folders with the plate name as to avoid conflicts. The files are renamed after analysis to include the plate prefix.

# ## Import libraries

# In[1]:


import pathlib


# ## Set path to directory with CellProfiler output

# In[2]:


# directory where SQLite files are located in folders per plate
sqlite_dir = pathlib.Path("../2.cellprofiler_analysis/analysis_output/")


# ## Add plate prefix to all SQLite files

# In[3]:


# iterate through all folders in directory to get paths to each SQLite file
for file_path in sqlite_dir.rglob('*.sqlite'):
    # if the SQLite files already start with `Plate`, then the file has already been renamed
    if str(file_path.stem).startswith("Plate"):
        print(f"{file_path.name} already has the `Plate` prefix, which means it was already corrected.")
        continue
    # create new file name where the folder name is included as the prefix
    new_file_name = f"{file_path.parent.name}_{file_path.name}"
    # create a new path with the new name
    new_path = file_path.with_name(new_file_name)
    # rename all SQLite files by using the new path
    file_path.rename(new_path)
    print(f"Plate name prefix has been added to {file_path}. The new name is {new_path}.")

