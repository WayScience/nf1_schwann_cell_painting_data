"""
These collection of functions runs CellProfiler and renames the .sqlite outputs to any specified name if 
running an analysis pipeline.
"""

# must use the annotations import as CellProfiler is restricted to Python 3.8 at this time so Optional
# by itself only works in Python 3.10
from __future__ import annotations
from typing import Optional
import os
import subprocess
import pathlib


def rename_sqlite_file(sqlite_dir_path: pathlib.Path, name: str):
    """Rename the .sqlite file into {name}.sqlite as to differentiate between different files.

    Args:
        sqlite_dir_path (pathlib.Path): path to CellProfiler_output directory
        name (str): new name for the SQLite file

    Raises:
        FileNotFoundError: This error will occur if no .sqlite file is found in the specified directory.
        This means that this function cannot find a file to rename, so it raises an error.
    """
    try:
        # Find the first .sqlite file in the directory
        sqlite_file_path = next(sqlite_dir_path.glob("*.sqlite"))

        # Create a new file name with the specified name
        new_file_name = sqlite_dir_path / f"{name}_nf1_analysis.sqlite"

        # Change the file name in the directory
        sqlite_file_path.rename(new_file_name)
        print(f"The file is renamed to {new_file_name.name}!")

    except StopIteration:
        # Handle case where no .sqlite file is found
        raise FileNotFoundError(
            f"No .sqlite file found in the directory: {sqlite_dir_path}"
        )


def run_cellprofiler(
    path_to_pipeline: str,
    path_to_output: str,
    path_to_images: str,
    sqlite_name: Optional[None | str] = None,
    analysis_run: Optional[False | bool] = False,
):
    """Run CellProfiler on data. It can be used for either a illumination correction pipeline (default) and analysis pipeline (when
    parameter is set to True).

    Args:
        path_to_pipeline (str): path to the CellProfiler .cppipe file with the segmentation and feature measurement modules
        path_to_output (str): path to the output folder
        path_to_images (str): path to the images
        sqlite_name (str, optional): string with name for SQLite file for an analysis pipeline if you plan on running
        multiple sets of images (e.g., per plate) so that the outputs will have different names (default is None)
        analysis_run (bool, optional): will use functions to complete an analysis pipeline (default is False)
    """
    # check to make sure paths to pipeline and directory of images are correct before running the pipeline
    if not pathlib.Path(path_to_pipeline):
        raise FileNotFoundError(
            f"The file '{pathlib.Path(path_to_pipeline).name}' does not exist"
        )
    if not pathlib.Path(path_to_images).is_dir():
        raise FileNotFoundError(
            f"Directory '{pathlib.Path(path_to_images).name}' does not exist or is not a directory"
        )

    # make logs directory
    log_dir = pathlib.Path("./logs")
    os.makedirs(log_dir, exist_ok=True)

    # make output directory if it is not already created
    os.makedirs(path_to_output, exist_ok=True)

    # run CellProfiler illumination correction pipeline
    if not analysis_run:
        print(f"Starting CellProfiler run on {pathlib.Path(path_to_images).name}")
        # a log file is created for each plate or data set name (based on folder name with images) that holds all outputs and errors
        with open(
            pathlib.Path(
                f"logs/cellprofiler_output_{pathlib.Path(path_to_images).name}.log"
            ),
            "w",
        ) as cellprofiler_output_file:
            # run CellProfiler for a illumination correction pipeline
            command = [
                "cellprofiler",
                "-c",
                "-r",
                "-p",
                path_to_pipeline,
                "-o",
                path_to_output,
                "-i",
                path_to_images,
            ]
            subprocess.run(
                command,
                stdout=cellprofiler_output_file,
                stderr=cellprofiler_output_file,
                check=True,
            )
            print(
                f"The CellProfiler run has been completed with {pathlib.Path(path_to_images).name}. Please check log file for any errors."
            )

    # run CellProfiler analysis pipeline
    if analysis_run:
        if sqlite_name is None:
            raise ValueError(
                "You have not set a name for the SQLite file. Please add a sqlite_name for the analysis output."
            )
        # runs through any files that are in the output path
        if any(
            files.name.startswith(sqlite_name)
            for files in pathlib.Path(path_to_output).iterdir()
        ):
            print("This plate has already been analyzed!")
            return

        # run CellProfiler on corrected images
        print(f"Starting CellProfiler analysis run on {sqlite_name}")
        # A log file is created for each plate or data set name (based on folder name with images) that holds all outputs and errors
        with open(
            f"logs/cellprofiler_output_analysis_{sqlite_name}.log", "w"
        ) as cellprofiler_output_file:
            command = [
                "cellprofiler",
                "-c",
                "-r",
                "-p",
                path_to_pipeline,
                "-o",
                path_to_output,
                "-i",
                path_to_images,
            ]
            subprocess.run(
                command,
                stdout=cellprofiler_output_file,
                stderr=cellprofiler_output_file,
                check=True,
            )
            print(
                f"The CellProfiler run has been completed with {pathlib.Path(path_to_images).name}. Please check log file for any errors."
            )

        if sqlite_name:
            # rename the outputted .sqlite file as a specified name (used when running multiple plates with same CP pipeline)
            rename_sqlite_file(
                sqlite_dir_path=pathlib.Path(path_to_output), name=sqlite_name
            )
