import os
import glob
import pathlib
import shutil
import urllib.request
import zipfile


def download_figshare(
    figshare_id: str,
    output_file: pathlib.Path,
    metadata_dir: pathlib.Path,
    figshare_url: str = "https://ndownloader.figshare.com/files/",
    unzip_download: bool = False,
    output_dir: pathlib.Path = None,
):
    """
    Download the provided figshare resource and extract the files from Figshare. Extract the downloaded
    zip file into a folder and then seperate the metadata for each plate into a seperate metadata folder.

    Attributes
    ----------
    figshare_id : str
        string of numbers that corresponds to the figshare identifier
    output_file : pathlib.Path
        the location and file/folder name for the downloaded contents from Figshare (in the case of zip files, this will be a temp folder and is removed
        after extraction). In the case of downloading a zip file, this would be the name of the zip file.
    metadata_dir : pathlib.Path
        path to directory for metadata
    figshare_url: str, default "https://ndownloader.figshare.com/files/"
        the location of where the figshare id is stored
    unzip_download: bool, default False
        if set to True, then the expected download from Figshare is a zip file which will be unzipped
    output_dir : pathlib.Path, optional
        path to directory to extract images and metadata from zip file to
    """
    # access the url and download the zip file from figshare containing files for plate (images + metadata)
    urllib.request.urlretrieve(f"{figshare_url}/{figshare_id}", output_file)

    if unzip_download:
        # find the zip file downloaded from figshare and then extract it into the specific folder
        with zipfile.ZipFile(output_file, "r") as zip_files:
            zip_files.extractall(output_dir)

        # remove the zip file from the directory
        os.remove(output_file)
        print(
            f"The downloaded zip file contents have been extracted into {output_dir.name} folder for plate with ID {str(figshare_id)}!"
        )
    else:
        print("No files were extracted. Check to see if a zip file was downloaded.")

    # glob the metadata files together to then copy and remove
    metadata_files = glob.glob(f"{output_dir}/*.csv")
    for files in metadata_files:
        # copy the metadata downloaded from Figshare into the metadata dir (must use ../ to go back one to access this directory from the plate folder)
        # which will overwrite the GitHub versioned metadata
        shutil.copy(files, str(metadata_dir))
        # remove the metadata from the plate directory to make it an images only directory
        os.remove(files)
    print("The metadata has been moved into its own directory!")


def extract_zip_from_Figshare(
    path_to_zip_file: pathlib.Path, extraction_path: pathlib.Path
):
    """
    This function will extract images from zip files downloaded from Figshare. This function is used if
    multiple plates are in the same item on Figshare.

    Attributes
    ----------
        path_to_zip_file (pathlib.Path):
            path to extracted zip files from Figshare
        extraction_path (pathlib.Path):
            path to directory for zip file contents (images) to be extracted to
    """
    # make output directory if it is not already created
    os.makedirs(extraction_path, exist_ok=True)

    # extract images from zip file(s) downloaded from figshare into specific directory
    with zipfile.ZipFile(path_to_zip_file, "r") as zip_file:
        zip_file.extractall(extraction_path)
        
    print(f"All images/files within the zip file have been extracted to {extraction_path.name}!")
