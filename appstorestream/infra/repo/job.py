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
# Modified   : Sunday July 28th 2024 02:11:32 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from abc import ABC, abstractmethod
import pandas as pd
from appstorestream.application.base.job import Job, JobMeta
from appstorestream.application.appdata.job import AppDataJob
from appstorestream.application.base.repo import AppLayerRepo
from appstorestream.core.enum import Stage
from
from appstorestream.infra.database.mysql import MySQLDatabase

# ------------------------------------------------------------------------------------------------ #
#                                    JOB REPO                                                      #
# ------------------------------------------------------------------------------------------------ #

class JobRepo(AppLayerRepo):
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
            db.insert(data=job.as_df(), tablename=self.__tablename)


    @abstractmethod
    def get(self, id: int) -> pd.DataFrame:
        """
        Fetches data from the 'job' table based on the category_id.

        Args:
            id (int): The ID of the job.

        Returns:
            pd.DataFrame: A DataFrame containing the data for the specified category.
        """

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

    def delete(self, id: int) -> None:
        """
        Deletes records from the 'job' table based on the category_id.

        Args:
            id (int): The ID of the job to delete records for.

        Raises:
            ValueError: If attempting to delete from a permanent database.
        """

        # Construct SQL query for deletion
        query = """
        DELETE FROM job
        WHERE job_id = :job_id;
        """
        params = {'job_id': id}

        # Use the database connection to execute the delete query
        with self._database as conn:
            return conn.execute(query, params)

# ------------------------------------------------------------------------------------------------ #
#                                    APPDATA JOB REPO                                              #
# ------------------------------------------------------------------------------------------------ #
class AppDataJobRepo(JobRepo):
    def get(self, id: int) -> AppDataJob:
        """
        Fetches data from the 'job' table based on job id.

        Args:
            id (int): The ID of the job.

        Returns:
            AppDataJob: An AppDataJob object.
        """

        query = """
        SELECT * FROM job
        WHERE job_id = :job_id;
        """
        params = {'job_id': id}

        # Use the database connection to execute the query and return the result as a DataFrame
        with self._database as conn:
            job_data = conn.query(query, params)
            try:
                jobmeta = JobMeta(**job_data.iloc[0].to_dict())
                return AppDataJob(jobmeta=jobmeta)
            except KeyError as e:
                raise ValueError(f"Job id: {id} was not found.")