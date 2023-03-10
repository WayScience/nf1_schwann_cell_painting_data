import os
import glob
import pathlib
import shutil
import urllib.request
import zipfile


def download_figshare(
    figshare_id: str,
    output_file: pathlib.Path,
    output_dir: pathlib.Path,
    metadata_dir: pathlib.Path,
    figshare_url: str = "https://ndownloader.figshare.com/files/",
    unzip_files: bool = False,
):
    """
    Download the provided figshare resource and extract the files from Figshare. Extract the downloaded
    zip file into a folder and then seperate the metadata for each plate into a seperate metadata folder.

    Attributes
    ----------
    figshare_id : str
        string of numbers that corresponds to the figshare identifier
    output_file : pathlib.Path
        the location and file name for the downloaded contents from Figshare
    output_dir : pathlib.Path
        path to directory for images
    metadata_dir : pathlib.Path
        path to directory for metadata
    figshare_url: str, default "https://ndownloader.figshare.com/files/"
        the location of where the figshare id is stored
    unzip_files: bool, default False
        if set to True, then the expected download from Figshare is a zip file which will be unzipped
    """
    # access the url and download the zip file from figshare containing files for plate (images + metadata)
    urllib.request.urlretrieve(f"{figshare_url}/{figshare_id}", output_file)

    if unzip_files==True:
    # find the zip file and then extract it into the specific folder
        with zipfile.ZipFile(output_file, "r") as zip_files:
            zip_files.extractall(output_dir)

        # remove the zip file from the directory
        os.remove(output_file)
        print(
            f"The files have been extracted into {output_dir.name} folder for plate with ID {str(figshare_id)}!"
        )
    else:
        print(
            f"The files have been downloaded into {output_dir.name} folder for plate with ID {str(figshare_id)}!"
        )

    # glob the metadata files together to then copy and remove
    metadata_files = glob.glob(f'{output_dir}/*.csv')
    for files in metadata_files:
        # copy the metadata downloaded from Figshare into the metadata dir (must use ../ to go back one to access this directory from the plate folder) 
        # which will overwrite the GitHub versioned metadata
        shutil.copy(files, str(metadata_dir))
        # remove the metadata from the plate directory to make it an images only directory
        os.remove(files)
    print("The metadata has been moved into its own directory!")
