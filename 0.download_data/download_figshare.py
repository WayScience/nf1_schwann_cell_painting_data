import os
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
):
    """
    Download the provided figshare resource and extract the files from Figshare. Extract the downloaded
    zip file into a folder and then seperate the metadata for each plate into a seperate metadata folder.

    Attributes
    ----------
    figshare_id : str
        string of numbers that corresponds to the figshare identifier
    output_file : pathlib.Path
        the location and file name of the downloaded zip file
    output_dir : pathlib.Path
        path to directory for images
    metadata_dir : pathlib.Path
        path to directory for metadata
    figshare_url: str, default "https://ndownloader.figshare.com/files/"
        the location of where the figshare id is stored
    """
    # access the url and download the zip file from figshare containing files for plate (images + metadata)
    urllib.request.urlretrieve(f"{figshare_url}/{figshare_id}", output_file)

    # find the zip file and then extract it into the specific folder
    with zipfile.ZipFile(output_file, "r") as zip_files:
        zip_files.extractall(output_dir)

    # remove the zip file from the directory
    os.remove(output_file)
    print(
        f"The files have been downloaded into {output_dir.name} folder for plate with ID {str(figshare_id)}!"
    )

    # move the metadata files into a new folder from the images
    for files in output_dir.iterdir():
        if str(files).endswith("csv"):
            shutil.move(str(files), str(metadata_dir))
    print("The metadata has been moved into its own directory!")
