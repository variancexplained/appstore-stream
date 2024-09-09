#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/repo/monitor/x4mload.py                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday September 6th 2024 07:42:43 am                                               #
# Modified   : Saturday September 7th 2024 11:10:49 pm                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

import logging
from typing import Any, Dict

import pandas as pd

from appvocai.core.enum import DataType, StageType
from appvocai.domain.monitor.x4mload import X4MLoadMetrics
from appvocai.domain.repo.base import Repo
from appvocai.infra.database.mysql import MySQLDatabase

# ------------------------------------------------------------------------------------------------ #
#                                  EXTRACT METRICS REPO                                            #
# ------------------------------------------------------------------------------------------------ #


class X4MLoadMetricsRepo(Repo):
    """
    Repository class for managing X4MLoadMetrics data in the 'metrics' table.

    This class provides methods for adding metrics, retrieving specific metrics by job, task, data type, and task type,
    and querying the entire metrics table. It interacts with a MySQL database to perform these stages.

    Attributes:
    ----------
    __table_name : str
        The name of the table where metrics are stored. This is a private attribute and is set to "metrics".

    _database : MySQLDatabase
        An instance of MySQLDatabase that is used to interact with the database.

    Methods:
    -------
    __len__() -> int
        Returns the total count of records in the 'metrics' table by retrieving all records.

    add(metrics: X4MLoadMetrics) -> None
        Adds a new X4MLoadMetrics record to the database. The metrics are converted to a dictionary using
        `as_dict()` method and inserted into the 'metrics' table.

    get_job_metrics(job_id: int) -> pd.DataFrame
        Retrieves metrics for a specific job by `job_id` and returns them as a Pandas DataFrame.

    get_task_metrics(task_id: int) -> pd.DataFrame
        Retrieves metrics for a specific task by `task_id` and returns them as a Pandas DataFrame.

    get_data_type_metrics(data_type: DataType) -> pd.DataFrame
        Retrieves metrics based on the `data_type` and returns them as a Pandas DataFrame.

    get_stage_type_metrics(stage_type: StageType) -> pd.DataFrame
        Retrieves metrics based on the `stage_type` and returns them as a Pandas DataFrame.

    getall() -> pd.DataFrame
        Retrieves all records from the 'metrics' table and returns them as a Pandas DataFrame.
    """

    __table_name = "metrics"

    def __init__(self, database: MySQLDatabase) -> None:
        """
        Initializes the X4MLoadMetricsRepo with a MySQLDatabase instance.

        Parameters:
        ----------
        database : MySQLDatabase
            The database connection used for executing queries.
        """
        super().__init__()
        self._database = database
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def __len__(self) -> int:
        """
        Returns the number of records in the 'metrics' table.

        Returns:
        -------
        int
            The total number of records in the table.
        """
        return len(self.getall())

    def add(self, metrics: X4MLoadMetrics) -> None:
        """
        Inserts a new X4MLoadMetrics record into the 'metrics' table.

        Parameters:
        ----------
        metrics : X4MLoadMetrics
            The X4MLoadMetrics object containing the data to be inserted. This data is transformed into a dictionary
            using the `as_dict()` method and passed to the SQL insert query.
        """
        query = """
                INSERT INTO metrics (
                    project_id, job_id,  task_id, data_type, stage_type, dt_started, dt_ended, duration, instances,
                    latency_min, latency_average, latency_median, latency_max, latency_std,
                    throughput_min, throughput_average, throughput_median, throughput_max, throughput_std
                ) VALUES (
                    :project_id, :job_id, :task_id, :data_type, :stage_type, :dt_started, :dt_ended, :duration, :instances,
                    :latency_min, :latency_average, :latency_median, :latency_max, :latency_std,
                    :throughput_min, :throughput_average, :throughput_median, :throughput_max, :throughput_std
                );"""
        params = metrics.as_dict()

        with self._database as db:
            db.execute(query=query, params=params)

    def get(self, id: int) -> X4MLoadMetrics:
        raise NotImplementedError

    def get_all(self) -> pd.DataFrame:
        """
        Retrieves metrics for a specific job by its job_id.

        Parameters:
        ----------
        job_id : int
            The ID of the job for which to retrieve metrics.

        Returns:
        -------
        pd.DataFrame
            A Pandas DataFrame containing the metrics for the specified job.
        """
        query = """
        SELECT  project_id,
                job_id,
                task_id,
                data_type,
                stage_type,
                dt_started,
                dt_ended,
                duration,
                instances,
                latency_min,
                latency_average,
                latency_median,
                latency_max,
                latency_std,
                throughput_min,
                throughput_average,
                throughput_median,
                throughput_max,
                throughput_std
                      FROM metrics;
        """
        params: Dict[str, Any] = {}

        with self._database as db:
            return db.query(query=query, params=params)

    def get_job_metrics(self, job_id: int) -> pd.DataFrame:
        """
        Retrieves metrics for a specific job by its job_id.

        Parameters:
        ----------
        job_id : int
            The ID of the job for which to retrieve metrics.

        Returns:
        -------
        pd.DataFrame
            A Pandas DataFrame containing the metrics for the specified job.
        """
        query = """
        SELECT  project_id,
                job_id,
                task_id,
                data_type,
                stage_type,
                dt_started,
                dt_ended,
                duration,
                instances,
                latency_min,
                latency_average,
                latency_median,
                latency_max,
                latency_std,
                throughput_min,
                throughput_average,
                throughput_median,
                throughput_max,
                throughput_std
            FROM metrics;
        WHERE job_id = :job_id;
        """
        params = {"job_id": job_id}

        with self._database as db:
            return db.query(query=query, params=params)

    def get_task_metrics(self, task_id: int) -> pd.DataFrame:
        """
        Retrieves metrics for a specific task by its task_id.

        Parameters:
        ----------
        task_id : int
            The ID of the task for which to retrieve metrics.

        Returns:
        -------
        pd.DataFrame
            A Pandas DataFrame containing the metrics for the specified task.
        """
        query = """
        SELECT  project_id,
                job_id,
                task_id,
                data_type,
                stage_type,
                dt_started,
                dt_ended,
                duration,
                instances,
                latency_min,
                latency_average,
                latency_median,
                latency_max,
                latency_std,
                throughput_min,
                throughput_average,
                throughput_median,
                throughput_max,
                throughput_std
            FROM metrics;
        WHERE task_id = :task_id;
        """
        params = {"task_id": task_id}

        with self._database as db:
            return db.query(query=query, params=params)

    def get_data_type_metrics(self, data_type: DataType) -> pd.DataFrame:
        """
        Retrieves metrics based on the specified data type.

        Parameters:
        ----------
        data_type : DataType
            The type of data for which to retrieve metrics (e.g., AppData, Reviews).

        Returns:
        -------
        pd.DataFrame
            A Pandas DataFrame containing the metrics for the specified data type.
        """
        query = """
        SELECT  project_id,
                job_id,
                task_id,
                data_type,
                stage_type,
                dt_started,
                dt_ended,
                duration,
                instances,
                latency_min,
                latency_average,
                latency_median,
                latency_max,
                latency_std,
                throughput_min,
                throughput_average,
                throughput_median,
                throughput_max,
                throughput_std
            FROM metrics;
        WHERE data_type = :data_type;
        """
        params = {"data_type": data_type.value}

        with self._database as db:
            return db.query(query=query, params=params)

    def get_stage_type_metrics(self, stage_type: StageType) -> pd.DataFrame:
        """
        Retrieves metrics based on the specified task type.

        Parameters:
        ----------
        stage_type : StageType
            The type of task for which to retrieve metrics (e.g., Review, Load).

        Returns:
        -------
        pd.DataFrame
            A Pandas DataFrame containing the metrics for the specified task type.
        """
        query = """
        SELECT  project_id,
                job_id,
                task_id,
                data_type,
                stage_type,
                dt_started,
                dt_ended,
                duration,
                instances,
                latency_min,
                latency_average,
                latency_median,
                latency_max,
                latency_std,
                throughput_min,
                throughput_average,
                throughput_median,
                throughput_max,
                throughput_std
            FROM metrics;
        WHERE stage_type = :stage_type;
        """
        params = {"stage_type": stage_type.value}

        with self._database as db:
            return db.query(query=query, params=params)

    def getall(self) -> pd.DataFrame:
        """
        Retrieves all metrics from the 'metrics' table.

        Returns:
        -------
        pd.DataFrame
            A Pandas DataFrame containing all the records from the metrics table.
        """
        query = """
        SELECT  project_id,
                job_id,
                task_id,
                data_type,
                stage_type,
                dt_started,
                dt_ended,
                duration,
                instances,
                latency_min,
                latency_average,
                latency_median,
                latency_max,
                latency_std,
                throughput_min,
                throughput_average,
                throughput_median,
                throughput_max,
                throughput_std
            FROM metrics;
        """
        params: Dict[str, Any] = {}

        with self._database as db:
            return db.query(query=query, params=params)

    def remove_job_metrics(self, job_id: int) -> None:
        confirm = input(
            f"Please confirm removal of metrics for job {job_id}. This is irreversable. Y/N"
        )
        if "y" in confirm.lower():
            query = """
                DELETE FROM metrics
                WHERE job_id = :job_id;
            """
            params = {"job_id": job_id}

            with self._database as db:
                db.execute(query=query, params=params)
        else:
            msg = f"Removal of metrics for job {job_id} aborted."
            self._logger.info(msg)

    def remove_all(self) -> None:
        confirm = input(
            "Please confirm removal of all metrics. This is irreversable. Y/N"
        )
        if "y" in confirm.lower():
            query = """
                DELETE FROM metrics;
            """
            params: Dict[str, Any] = {}

            with self._database as db:
                db.execute(query=query, params=params)
        else:
            msg = "Removal of metrics aborted."
            self._logger.info(msg)
