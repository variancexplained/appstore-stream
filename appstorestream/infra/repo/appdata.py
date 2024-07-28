#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/repo/appdata.py                                               #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 10:27:12 pm                                                 #
# Modified   : Saturday July 27th 2024 02:35:02 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from dataclasses import dataclass

import pandas as pd

from appstorestream.core.enum import DatabaseSet
from appstorestream.domain.repo import Repo
from appstorestream.infra.database.mysql import MySQLDatabase


# ------------------------------------------------------------------------------------------------ #
class AppDataExtractRepo(Repo):
    """Repository class for handling operations on the 'appdata' table.

    Args:
        database (MySQLDatabase): The database instance used for operations.
    """

    __tablename = "appdata"

    def __init__(self, database: MySQLDatabase) -> None:
        """
        Initializes the AppDataExtractRepo with a database connection.

        """
        super().__init__()
        self._database = database

    def add(self, appdata: pd.DataFrame) -> None:
        """Adds AppData to the repository

        Args:
            appdata (pd.DataFrame):  AppData in DataFrame format.
        """
        with self._database as db:
            db.insert(data=appdata)

    def get(self, category_id: int) -> pd.DataFrame:
        """
        Fetches data from the 'appdata' table based on the category_id.

        Args:
            category_id (int): The ID of the category to fetch data for.

        Returns:
            pd.DataFrame: A DataFrame containing the data for the specified category.
        """
        # Construct SQL query using the category_id
        query = """
        SELECT * FROM appdata
        WHERE category_id = :category_id
        """
        params = {'category_id': category_id}

        # Use the database connection to execute the query and return the result as a DataFrame
        with self._database as conn:
            return conn.query(query, params)

    def insert(self, data: pd.DataFrame, dtype: dict = None) -> int:
        """
        Inserts data into the 'appdata' table.

        Args:
            data (pd.DataFrame): DataFrame containing the data to insert.
            dtype (dict, optional): Dictionary specifying data types for columns.

        Returns:
            int: Number of rows inserted.
        """
        with self._database as conn:
            return conn.insert(data, tablename=self.__tablename, dtype=dtype)

    def upsert(self, data: pd.DataFrame) -> int:
        """
        Upserts (inserts or updates) data into the 'appdata' table.

        Args:
            data (pd.DataFrame): DataFrame containing the data to upsert.

        Returns:
            int: Number of rows affected by the upsert operation.
        """
        # Convert DataFrame to a list of dictionaries for upsert operation
        data_dict = data.to_dict(orient='records')

        # Construct the upsert SQL query
        upsert_query = """
        INSERT INTO appdata (
            id, name, description, category_id, developer_id, developer_name,
            developer_view_url, seller_name, seller_url, price, currency,
            rating_average, rating_average_current_version, rating_count,
            rating_count_current_version, app_url, screenshot_urls,
            release_date, release_date_current_version, version, date_extracted
        ) VALUES (
            :id, :name, :description, :category_id, :developer_id, :developer_name,
            :developer_view_url, :seller_name, :seller_url, :price, :currency,
            :rating_average, :rating_average_current_version, :rating_count,
            :rating_count_current_version, :app_url, :screenshot_urls,
            :release_date, :release_date_current_version, :version, :date_extracted
        ) ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            description = VALUES(description),
            category_id = VALUES(category_id),
            developer_id = VALUES(developer_id),
            developer_name = VALUES(developer_name),
            developer_view_url = VALUES(developer_view_url),
            seller_name = VALUES(seller_name),
            seller_url = VALUES(seller_url),
            price = VALUES(price),
            currency = VALUES(currency),
            rating_average = VALUES(rating_average),
            rating_average_current_version = VALUES(rating_average_current_version),
            rating_count = VALUES(rating_count),
            rating_count_current_version = VALUES(rating_count_current_version),
            app_url = VALUES(app_url),
            screenshot_urls = VALUES(screenshot_urls),
            release_date = VALUES(release_date),
            release_date_current_version = VALUES(release_date_current_version),
            version = VALUES(version),
            date_extracted = VALUES(date_extracted);
        """

        # Execute the upsert query for each record
        with self._database as conn:
            upsert_count = 0
            for record in data_dict:
                result = conn.execute(upsert_query, record)
                upsert_count += result.rowcount
            return upsert_count

    def delete(self, category_id: int) -> None:
        """
        Deletes records from the 'appdata' table based on the category_id.

        Args:
            category_id (int): The ID of the category to delete records for.

        Raises:
            ValueError: If attempting to delete from a permanent database.
        """
        # Check if the database is permanent and raise an exception if so
        if self._database.dbset == DatabaseSet.PERMANENT:
            msg = "Delete from the permanent database is not permitted."
            self._logger.exception(msg)
            raise ValueError(msg)

        # Construct SQL query for deletion
        query = """
        DELETE FROM appdata
        WHERE category_id = :category_id
        """
        params = {'category_id': category_id}

        # Use the database connection to execute the delete query
        with self._database as conn:
            return conn.execute(query, params)
