#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/repo/metrics/extract.py                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday September 6th 2024 07:42:43 am                                               #
# Modified   : Friday September 6th 2024 10:46:37 am                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

import logging
from typing import Any, Dict

import pandas as pd
from sqlalchemy.types import BIGINT, DATETIME, FLOAT, INTEGER, VARCHAR

from appvocai.core.enum import DataType, TaskType
from appvocai.domain.metrics.extract import ExtractMetrics
from appvocai.domain.repo.base import Repo
from appvocai.infra.database.mysql import MySQLDatabase

# ------------------------------------------------------------------------------------------------ #
DTYPES = {
    "job_id": BIGINT,
    "data_type": VARCHAR(255),
    "task_id": VARCHAR(255),
    "task_type": VARCHAR(255),
    "instance_id": INTEGER,
    "dt_started": DATETIME,
    "dt_stopped": DATETIME,
    "duration": FLOAT,
    "instances": INTEGER,
    "latency_min": FLOAT,
    "latency_average": FLOAT,
    "latency_median": FLOAT,
    "latency_max": FLOAT,
    "latency_std": FLOAT,
    "throughput_min": FLOAT,
    "throughput_average": FLOAT,
    "throughput_median": FLOAT,
    "throughput_max": FLOAT,
    "throughput_std": FLOAT,
}
# ------------------------------------------------------------------------------------------------ #
#                                  EXTRACT METRICS REPO                                            #
# ------------------------------------------------------------------------------------------------ #


class ExtractMetricsRepo(Repo):
    """
    Repository class for managing ExtractMetrics data in the 'metrics' table.

    This class provides methods for adding metrics, retrieving specific metrics by job, task, data type, and task type,
    and querying the entire metrics table. It interacts with a MySQL database to perform these operations.

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

    add(metrics: ExtractMetrics) -> None
        Adds a new ExtractMetrics record to the database. The metrics are converted to a dictionary using
        `as_dict()` method and inserted into the 'metrics' table.

    get_job_metrics(job_id: int) -> pd.DataFrame
        Retrieves metrics for a specific job by `job_id` and returns them as a Pandas DataFrame.

    get_task_metrics(task_id: int) -> pd.DataFrame
        Retrieves metrics for a specific task by `task_id` and returns them as a Pandas DataFrame.

    get_data_type_metrics(data_type: DataType) -> pd.DataFrame
        Retrieves metrics based on the `data_type` and returns them as a Pandas DataFrame.

    get_task_type_metrics(task_type: TaskType) -> pd.DataFrame
        Retrieves metrics based on the `task_type` and returns them as a Pandas DataFrame.

    getall() -> pd.DataFrame
        Retrieves all records from the 'metrics' table and returns them as a Pandas DataFrame.
    """

    __table_name = "metrics"

    def __init__(self, database: MySQLDatabase) -> None:
        """
        Initializes the ExtractMetricsRepo with a MySQLDatabase instance.

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

    def add(self, metrics: ExtractMetrics) -> None:
        """
        Inserts a new ExtractMetrics record into the 'metrics' table.

        Parameters:
        ----------
        metrics : ExtractMetrics
            The ExtractMetrics object containing the data to be inserted. This data is transformed into a dictionary
            using the `as_dict()` method and passed to the SQL insert query.
        """
        query = """
                INSERT INTO metrics (
                    job_id, data_type, task_id, task_type, instance_id, dt_started, dt_stopped, duration, instances,
                    latency_min, latency_average, latency_median, latency_max, latency_std,
                    throughput_min, throughput_average, throughput_median, throughput_max, throughput_std,
                    f1, f2
                ) VALUES (
                    :job_id, :data_type, :task_id, :task_type, :request_id, :dt_started, :dt_stopped, :duration, :requests,
                    :latency_min, :latency_average, :latency_median, :latency_max, :latency_std,
                    :throughput_min, :throughput_average, :throughput_median, :throughput_max, :throughput_std,
                    :speedup, :size
                );"""
        params = metrics.as_dict()

        with self._database as db:
            db.execute(query=query, params=params)

    def get(self, id: int) -> ExtractMetrics:
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
        SELECT  job_id,
                data_type,
                task_id,
                task_type,
                instance_id,
                dt_started,
                dt_stopped,
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
                throughput_std,
                f1,
                f2
      FROM metrics;
        """
        params: Dict[str, Any] = {}

        with self._database as db:
            data = db.query(query=query, params=params)
            data.rename(
                columns={
                    "f1": "speedup",
                    "f2": "size",
                    "instance_id": "request_id",
                    "instances": "requests",
                }
            )
            return data

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
        SELECT  job_id,
                data_type,
                task_id,
                task_type,
                instance_id,
                dt_started,
                dt_stopped,
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
                throughput_std,
                f1,
                f2
      FROM metrics
        WHERE job_id = :job_id;
        """
        params = {"job_id": job_id}

        with self._database as db:
            data = db.query(query=query, params=params)
            data.rename(
                columns={
                    "f1": "speedup",
                    "f2": "size",
                    "instance_id": "request_id",
                    "instances": "requests",
                }
            )
            return data

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
        SELECT  job_id,
                data_type,
                task_id,
                task_type,
                instance_id,
                dt_started,
                dt_stopped,
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
                throughput_std,
                f1,
                f2
      FROM metrics
        WHERE task_id = :task_id;
        """
        params = {"task_id": task_id}

        with self._database as db:
            data = db.query(query=query, params=params)
            data.rename(
                columns={
                    "f1": "speedup",
                    "f2": "size",
                    "instance_id": "request_id",
                    "instances": "requests",
                }
            )
            return data

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
        SELECT  job_id,
                data_type,
                task_id,
                task_type,
                instance_id,
                dt_started,
                dt_stopped,
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
                throughput_std,
                f1,
                f2
      FROM metrics
        WHERE data_type = :data_type;
        """
        params = {"data_type": data_type.value}

        with self._database as db:
            data = db.query(query=query, params=params)
            data.rename(
                columns={
                    "f1": "speedup",
                    "f2": "size",
                    "instance_id": "request_id",
                    "instances": "requests",
                }
            )
            return data

    def get_task_type_metrics(self, task_type: TaskType) -> pd.DataFrame:
        """
        Retrieves metrics based on the specified task type.

        Parameters:
        ----------
        task_type : TaskType
            The type of task for which to retrieve metrics (e.g., Extract, Load).

        Returns:
        -------
        pd.DataFrame
            A Pandas DataFrame containing the metrics for the specified task type.
        """
        query = """
        SELECT  job_id,
                data_type,
                task_id,
                task_type,
                instance_id,
                dt_started,
                dt_stopped,
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
                throughput_std,
                f1,
                f2
      FROM metrics
        WHERE task_type = :task_type;
        """
        params = {"task_type": task_type.value}

        with self._database as db:
            data = db.query(query=query, params=params)
            data.rename(
                columns={
                    "f1": "speedup",
                    "f2": "size",
                    "instance_id": "request_id",
                    "instances": "requests",
                }
            )
            return data

    def getall(self) -> pd.DataFrame:
        """
        Retrieves all metrics from the 'metrics' table.

        Returns:
        -------
        pd.DataFrame
            A Pandas DataFrame containing all the records from the metrics table.
        """
        query = """
        SELECT  job_id,
                data_type,
                task_id,
                task_type,
                instance_id,
                dt_started,
                dt_stopped,
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
                throughput_std,
                f1,
                f2
        FROM metrics
        """
        params: Dict[str, Any] = {}

        with self._database as db:
            data = db.query(query=query, params=params)
            data.rename(
                columns={
                    "f1": "speedup",
                    "f2": "size",
                    "instance_id": "request_id",
                    "instances": "requests",
                }
            )
            return data

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
