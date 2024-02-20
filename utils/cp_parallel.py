"""
This collection of functions runs CellProfiler in parallel and can convert the results into log files
for each process.
"""

import multiprocessing
import logging
from typing import List
import os
import subprocess
import pathlib
from concurrent.futures import ProcessPoolExecutor, Future
from errors.exceptions import MaxWorkerError


def results_to_log(
    results: List[subprocess.CompletedProcess], log_dir: pathlib.Path, run_name: str
) -> None:
    """
    This function will take the list of subprocess.results from a CellProfiler parallelization run and
    convert into a log file for each process.

    Args:
        results (List[subprocess.CompletedProcess]): the outputs from a subprocess.run
        log_dir (pathlib.Path): directory for log files
        run_name (str): a given name for the type of CellProfiler run being done on the plates (example: whole image features)
    """
    # Access the command (args) and stderr (output) for each CompletedProcess object
    for result in results:
        # assign plate name and decode the CellProfiler output to use in log file
        plate_name = result.args[6].name
        output_string = result.stderr.decode("utf-8")

        # set log file name as plate name from command
        log_file_path = pathlib.Path(f"{log_dir}/{plate_name}_{run_name}_run.log")
        # print output to a log file for each plate to view after the run
        # set up logging configuration
        log_format = "[%(asctime)s] [Process ID: %(process)d] %(message)s"
        logging.basicConfig(
            filename=log_file_path, level=logging.INFO, format=log_format
        )

        # log plate name and output string
        logging.info(f"Plate Name: {plate_name}")
        logging.info(f"Output String: {output_string}")


def run_cellprofiler_parallel(
    plate_info_dictionary: dict,
    run_name: str,
) -> None:
    """
    This function utilizes multi-processing to run CellProfiler pipelines in parallel.

    Args:
        plate_info_dictionary (dict): dictionary with all paths for CellProfiler to run a pipeline
        run_name (str): a given name for the type of CellProfiler run being done on the plates (example: whole image features)

    Raises:
        FileNotFoundError: if paths to pipeline and images do not exist
    """
    # create a list of commands for each plate with their respective log file
    commands = []

    # make logs directory
    log_dir = pathlib.Path("./logs")
    os.makedirs(log_dir, exist_ok=True)

    # iterate through each plate in the dictionary
    for _, info in plate_info_dictionary.items():
        # set paths for CellProfiler
        path_to_pipeline = info["path_to_pipeline"]
        path_to_images = info["path_to_images"]
        path_to_output = info["path_to_output"]

        # check to make sure paths to pipeline and directory of images are correct before running the pipeline
        if not pathlib.Path(path_to_pipeline).resolve(strict=True):
            raise FileNotFoundError(
                f"The file '{pathlib.Path(path_to_pipeline).name}' does not exist"
            )
        if not pathlib.Path(path_to_images).is_dir():
            raise FileNotFoundError(
                f"Directory '{pathlib.Path(path_to_images).name}' does not exist or is not a directory"
            )
        # make output directory if it is not already created
        pathlib.Path(path_to_output).mkdir(exist_ok=True)

        # creates a command for each plate in the list
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
        # creates a list of commands
        commands.append(command)

    # set the number of CPUs/workers as the number of commands
    num_processes = len(commands)

    # make sure that the number of workers does not exceed the maximum number of workers for the machine
    if num_processes > multiprocessing.cpu_count():
        raise MaxWorkerError(
            "Exception occurred: The number of commands exceeds the number of CPUs/workers. Please reduce the number of commands."
        )

    # set parallelization executer to the number of commands
    executor = ProcessPoolExecutor(max_workers=num_processes)

    # creates a list of futures that are each CellProfiler process for each plate
    futures: List[Future] = [
        executor.submit(
            subprocess.run,
            args=command,
            capture_output=True,
        )
        for command in commands
    ]

    # the list of CompletedProcesses holds all the information from the CellProfiler run
    results: List[subprocess.CompletedProcess] = [future.result() for future in futures]

    print("All processes have been completed!")

    # for each process, confirm that the process completed succesfully and return a log file
    for result in results:
        plate_name = result.args[6].name
        # convert the results into log files
        results_to_log(results=results, log_dir=log_dir, run_name=run_name)
        if result.returncode == 1:
            print(
                f"A return code of {result.returncode} was returned for {plate_name}, which means there was an error in the CellProfiler run."
            )

    # to avoid having multiple print statements due to for loop, confirmation that logs are converted is printed here
    print("All results have been converted to log files!")
