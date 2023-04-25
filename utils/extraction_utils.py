"""
This file contains functions to add single cell count metadata into the returned files or before 
saving the dataframe. As well, there are functions to extract image features from the outputted 
sqlite file from CellProfiler (based on the functions from the cells.SingleCells class in Pycytominer).
"""

# must use the annotations import as CellProfiler is restricted to Python 3.8 at this time so Optional
# by itself only works in Python 3.10
from __future__ import annotations
from typing import Optional
import pathlib
import pandas as pd
from sqlalchemy import create_engine
import numpy as np


def add_single_cell_count_df(
    data_df: pd.DataFrame, well_column_name: str = "Metadata_Well"
) -> pd.DataFrame:
    """
    This function adds a column with the number of singles cells per well to a pandas dataframe.

    Args:
        data_df (pd.DataFrame):
            dataframe to add number of single cells to
        well_column_name (str):
            name of column for wells to use for finding single cell count (defaults to "Metadata_Well")

    Returns:
        pd.DataFrame:
            pandas dataframe with new metadata column with single cell count
    """
    merged_data = (
        data_df.groupby([well_column_name])[well_column_name]
        .count()
        .reset_index(name="Metadata_number_of_singlecells")
    )

    data_df = data_df.merge(merged_data, on=well_column_name)
    # pop out the column from the dataframe
    singlecell_column = data_df.pop("Metadata_number_of_singlecells")
    # insert the column as the second index column in the dataframe
    data_df.insert(2, "Metadata_number_of_singlecells", singlecell_column)

    return data_df


def add_sc_count_metadata_file(
    data_path: pathlib.Path,
    well_column_name: str = "Metadata_Well",
    file_type: str = "csv.gz",
):
    """
    This function loads in the saved file from Pycytominer or CytoTable (e.g. normalized, etc.), adds the single cell counts for
    each well as metadata, and saves the file to the same place (as the same file type)

    Args:
        data_path (pathlib.Path):
            path to data file to add single cell count on
        well_column_name (str):
            name of column for wells to use for finding single cell count (defaults to "Metadata_Well")
        file_type (str, optional):
            the file type of the data (options include parquet, csv, defaults to "csv.gz")
    """
    # load in data
    if file_type == "csv.gz":
        data_df = pd.read_csv(data_path, compression="gzip")
    if file_type == "parquet":
        data_df = pd.read_parquet(data_path)
    if file_type == "csv":
        data_df = pd.read_csv(data_path)

    # add single cell count as new metadata column
    data_df = add_single_cell_count_df(
        data_df=data_df, well_column_name=well_column_name
    )

    # save updated df to same path as the same file type
    if file_type == "parquet":
        data_df.to_parquet(data_path)
    if file_type == "csv.gz":
        data_df.to_csv(data_path, compression="gzip")
    if file_type == "csv":
        data_df.to_csv(data_path)


def load_sqlite_as_df(
    sqlite_file: str,
    image_table_name: str = "Per_Image",
) -> pd.DataFrame:
    """
    load in table with image feature data from sqlite file

    Parameters
    ----------
    sqlite_file : str
        string of path to the sqlite file
    image_table_name : str
        string of the name with the image feature data (default = "Per_Image")

    Returns
    -------
    pd.DataFrame:
        dataframe containing image feature data
    """
    engine = create_engine(sqlite_file)
    conn = engine.connect()

    image_query = f"select * from {image_table_name}"
    image_df = pd.read_sql(sql=image_query, con=conn)

    return image_df


def extract_image_features(
    image_feature_categories: list[str] or str,
    image_df: pd.DataFrame,
    image_cols: list[str] or str,
) -> pd.DataFrame:
    """Confirm that the input list of image features categories are present in the image table and then extract those features.
    This is pulled from Pycytominer cyto_utils util.py 'extract_image_features` and edited.

    Parameters
    ----------
    image_feature_categories : list of str or str
        input image feature group(s) to extract from the image table including the prefix (e.g. ["Image_Correlation", "Image_ImageQuality"])
    image_df : pd.Dataframe
        image dataframe from SQLite file 'Per_Image' table
    image_cols : list of str or str
        column(s) to select from the image df to include

    Returns
    -------
    image_features_df : pd.DataFrame
        dataframe with extracted image features
    """
    # extract image features from image_feature_categories
    image_features = list(
        image_df.columns[
            image_df.columns.str.startswith(tuple(image_feature_categories))
        ]
    )

    # Add image features to the image_df
    image_features_df = image_df[image_features]

    # Add image_cols and strata to the dataframe
    image_features_df = pd.concat(
        [image_df[list(np.union1d(image_cols))], image_features_df], axis=1
    )

    return image_features_df
