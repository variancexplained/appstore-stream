#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/repo/job.py                                                   #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 01:28:02 am                                                   #
# Modified   : Saturday July 27th 2024 02:32:08 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #

import pandas as pd

from appstorestream.application.base.job import Job
from appstorestream.application.base.repo import ApplicationRepo
from appstorestream.core.enum import Stage
from appstorestream.infra.database.mysql import MySQLDatabase

# ------------------------------------------------------------------------------------------------ #
#                                    JOB REPO                                                      #
# ------------------------------------------------------------------------------------------------ #


# ------------------------------------------------------------------------------------------------ #
class JobRepo(ApplicationRepo):
    """Repository class for handling operations on the 'job' table.

    Args:
        database (MySQLDatabase): The database instance used for operations.
    """

    __tablename = "job"

    def __init__(self, database: MySQLDatabase) -> None:
        """
        Initializes the AppDataExtractRepo with a database connection.

        """
        super().__init__()
        self._database = database

    def add(self, job: Job) -> None:
        """
        Adds Job objects to the repository.

        Args:
            job (Job): Job entity
        """

        with self._database as db:
            db.insert(data=job.as_df())


    def get(self, category_id: int) -> pd.DataFrame:
        """
        Fetches data from the 'job' table based on the category_id.

        Args:
            category_id (int): The ID of the category to fetch data for.

        Returns:
            pd.DataFrame: A DataFrame containing the data for the specified category.
        """
        # Construct SQL query using the category_id
        query = """
        SELECT * FROM job
        WHERE category_id = :category_id;
        """
        params = {'category_id': category_id}

        # Use the database connection to execute the query and return the result as a DataFrame
        with self._database as conn:
            return conn.query(query, params)

    def getall(self) -> pd.DataFrame:
        """
        Fetches all the data from the 'job' table in a DataFrame format.

        Returns:
            pd.DataFrame: A DataFrame containing the data for the specified category.
        """
        # Construct SQL query using the category_id
        query = """
        SELECT * FROM job;
        """
        params = {}

        # Use the database connection to execute the query and return the result as a DataFrame
        with self._database as conn:
            return conn.query(query, params)

    def delete(self, category_id: int) -> None:
        """
        Deletes records from the 'job' table based on the category_id.

        Args:
            category_id (int): The ID of the category to delete records for.

        Raises:
            ValueError: If attempting to delete from a permanent database.
        """
        # Check if the database is final and raise an exception if so
        if self._database.dbset == Stage.LOAD:
            msg = "Delete from the final database is not permitted."
            self._logger.exception(msg)
            raise ValueError(msg)

        # Construct SQL query for deletion
        query = """
        DELETE FROM job
        WHERE category_id = :category_id;
        """
        params = {'category_id': category_id}

        # Use the database connection to execute the delete query
        with self._database as conn:
            return conn.execute(query, params)
