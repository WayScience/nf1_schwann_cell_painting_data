"""
These collection of functions runs CellProfiler and renames the .sqlite outputs to any specified name if 
running an analysis pipeline.
"""

# must use the annotations import as CellProfiler is restricted to Python 3.8 at this time so Optional
# by itself only works in Python 3.10
from __future__ import annotations
from typing import Optional
import subprocess
import pathlib


def rename_sqlite_file(sqlite_dir_path: pathlib.Path, name: str):
    """Rename the .sqlite file into {name}.sqlite as to differentiate between different files.

    Args:
        sqlite_dir_path (pathlib.Path): path to CellProfiler_output directory
        name (str): new name for the SQLite file

    Raises:
        FileNotFoundError: This error will occur if you do not have a SQLite file with the hard coded file name in the specified directory.
        This means that this function can not find the right file to rename, so it raises an error.
    """
    try:
        # CellProfiler requires a name to be set in to pipeline, so regardless of plate or method, all sqlite files name are hardcoded
        sqlite_file_path = pathlib.Path(f"{sqlite_dir_path}/NF1_data.sqlite")

        new_file_name = str(sqlite_file_path).replace(
            sqlite_file_path.name, f"{name}.sqlite"
        )

        # change the file name in the directory
        pathlib.Path(sqlite_file_path).rename(pathlib.Path(new_file_name))
        print(f"The file is renamed to {pathlib.Path(new_file_name).name}!")

    except FileNotFoundError as e:
        print(
            f"The NF1_data.sqlite file is not found in directory. Either the pipeline wasn't ran properly or the file is already renamed.\n"
            f"{e}"
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
    print(f"Starting CellProfiler run on {pathlib.Path(path_to_images).name}")
    # A log file is created for each plate or data set name (based on folder name with images)
    with open(pathlib.Path(f"logs/cellprofiler_output_{pathlib.Path(path_to_images).name}.log"), "w") as cellprofiler_output_file:
        # run CellProfiler for a illumination correction pipeline
        command = f"cellprofiler -c -r -p {path_to_pipeline} -o {path_to_output} -i {path_to_images}"
        subprocess.run(command, shell=True, stdout=cellprofiler_output_file, stderr=cellprofiler_output_file)
    cellprofiler_output_file.close()

    if analysis_run:
        # runs through any files that are in the output path
        if any(
            files.name.startswith(sqlite_name)
            for files in pathlib.Path(path_to_output).iterdir()
        ):
            print("This plate has already been analyzed!")
            return

        # run CellProfiler on corrected images
        with open("cellprofiler_output_analysis.log", "w") as cellprofiler_output_file:
            command = f"cellprofiler -c -r -p {path_to_pipeline} -o {path_to_output} -i {path_to_images}"
            subprocess.run(command, shell=True, capture_output=True)
        cellprofiler_output_file.close()

        if sqlite_name:
            # rename the outputted .sqlite file as a specified name (used when running multiple plates with same CP pipeline)
            rename_sqlite_file(
                sqlite_dir_path=pathlib.Path(path_to_output), name=sqlite_name
            )
