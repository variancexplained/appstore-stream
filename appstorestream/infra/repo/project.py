#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/repo/project.py                                               #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Sunday July 28th 2024 12:53:41 pm                                                   #
# Modified   : Sunday July 28th 2024 02:01:34 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

import pandas as pd
from sqlalchemy import text

from appstorestream.application.base.project import Project
from appstorestream.application.base.repo import AppLayerRepo
from appstorestream.infra.database.mysql import MySQLDatabase

# ------------------------------------------------------------------------------------------------ #
#                                    PROEJCT REPO                                                  #
# ------------------------------------------------------------------------------------------------ #

class ProjectRepo(AppLayerRepo):
    """Repository class for handling operations on the 'project' table.

    Args:
        database (MySQLDatabase): The database instance used for operations.
    """

    __tablename = "project"

    def __init__(self, database: MySQLDatabase) -> None:
        """
        Initializes the AppDataExtractRepo with a database connection.

        """
        super().__init__()
        self._database = database

    def add(self, project: Project) -> None:
        """
        Adds Project objects to the repository.

        Args:
            project (Project): Project entity
        """

        with self._database as db:
            db.insert(data=project.as_df(), tablename=self.__tablename)

    def get(self, id: int) -> Project:
        """
        Fetches data from the 'project' table based on the category_id.

        Args:
            id (int): The ID of the project.

        Returns:
            pd.DataFrame: A DataFrame containing the data for the specified category.
        """

        query = """
        SELECT * FROM project
        WHERE project_id = :project_id;
        """
        params = {'project_id': id}

        # Use the database connection to execute the query and return the result as a DataFrame
        with self._database as conn:
            project_data = conn.query(query, params)
            try:
                return Project(**project_data.iloc[0].to_dict())
            except KeyError as e:
                raise ValueError(f"Project id: {id} was not found.")


    def getall(self) -> pd.DataFrame:
        """
        Fetches all the data from the 'project' table in a DataFrame format.

        Returns:
            pd.DataFrame: A DataFrame containing the data for the specified category.
        """
        # Construct SQL query using the category_id
        query = """
        SELECT * FROM project;
        """
        params = {}

        # Use the database connection to execute the query and return the result as a DataFrame
        with self._database as conn:
            return conn.query(query, params)

    def update(self, project: Project) -> None:
        query = text("""
        UPDATE project
        SET dataset = :dataset, category_id = :category_id, category = :category,
            project_priority = :project_priority, progress = :progress, n_jobs = :n_jobs,
            last_job_id = :last_job_id, dt_last_job = :dt_last_job, project_status = :project_status
        WHERE project_id = :project_id
        """)
        params = {
            'dataset': project.dataset.value,
            'category_id': project.category_id,
            'category': project.category,
            'project_priority': project.project_priority,
            'progress': project.progress,
            'n_jobs': project.n_jobs,
            'last_job_id': project.last_job_id,
            'dt_last_job': project.dt_last_job.strftime('%Y-%m-%d %H:%M:%S') if project.dt_last_job else None,
            'project_status': project.project_status.value,
            'project_id': project.project_id,
        }
        with  self._database as conn:
            conn.execute(query=query, params=params)