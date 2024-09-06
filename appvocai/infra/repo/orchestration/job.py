#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/repo/orchestration/job.py                                           #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 01:28:02 am                                                   #
# Modified   : Friday September 6th 2024 05:45:34 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Job Repository Module"""
import pandas as pd

from appvocai.application.base.job import Job
from appvocai.application.base.repo import AppLayerRepo
from appvocai.core.enum import Dataset
from appvocai.infra.database.mysql import MySQLDatabase

# ------------------------------------------------------------------------------------------------ #
#                                    JOB REPO                                                      #
# ------------------------------------------------------------------------------------------------ #


class JobRepo(AppLayerRepo):
    """Repository class for handling operations on the 'job' table.

    Args:
        database (MySQLDatabase): The database instance used for operations.
    """

    __table_name = "job"

    def __init__(self, database: MySQLDatabase) -> None:
        """
        Initializes the AppDataExtractRepo with a database connection.

        """
        super().__init__()
        self._database = database

    def add(self, job: Job) -> Job:
        """
        Adds Job objects to the repository.

        Args:
            job (Job): Job entity
        """
        jobdata = job.as_dict()

        query = """
        INSERT INTO job (
            project_id,
            dataset,
            category_id,
            category,
            job_name,
            dt_created,
            dt_scheduled,
            dt_started,
            dt_ended,
            max_requests,
            batch_size,
            bookmark,
            runtime,
            request_count,
            record_count,
            request_throughput,
            record_throughput,
            total_errors,
            redirect_errors,
            client_errors,
            server_errors,
            data_errors,
            job_status,
            circuit_breaker_closed_burnin_period,
            circuit_breaker_closed_failure_rate_threshold,
            circuit_breaker_closed_window_size,
            circuit_breaker_half_open_delay,
            circuit_breaker_half_open_failure_rate_threshold,
            circuit_breaker_half_open_window_size,
            circuit_breaker_open_cooldown_period,
            circuit_breaker_short_circuit_404s_failure_rate_threshold,
            circuit_breaker_short_circuit_404s_window_size,
            circuit_breaker_short_circuit_errors_failure_rate_threshold,
            circuit_breaker_short_circuit_errors_window_size,
            request_async_session_max_concurrency,
            request_async_session_retries,
            request_async_session_timeout,
            request_athrottle_base_rate,
            request_athrottle_burn_in,
            request_athrottle_max_rate,
            request_athrottle_min_rate,
            request_athrottle_temperature,
            request_athrottle_window_size,
            request_generator_batch_size,

        ) VALUES (
            %(project_id)s,
            %(dataset)s,
            %(category_id)s,
            %(category)s,
            %(job_name)s,
            %(dt_created)s,
            %(dt_scheduled)s,
            %(dt_started)s,
            %(dt_ended)s,
            %(max_requests)s,
            %(batch_size)s,
            %(bookmark)s,
            %(runtime)s,
            %(request_count)s,
            %(record_count)s,
            %(request_throughput)s,
            %(record_throughput)s,
            %(total_errors)s,
            %(redirect_errors)s,
            %(client_errors)s,
            %(server_errors)s,
            %(data_errors)s,
            %(total_error_rate)s,
            %(redirect_error_rate)s,
            %(client_error_rate)s,
            %(server_error_rate)s,
            %(data_error_rate)s,
            %(unknown_error_rate)s,
            %(page_not_found_error_rate)s,
            %(job_status)s,
            %(circuit_breaker_closed_burnin_period)s,
            %(circuit_breaker_closed_failure_rate_threshold)s,
            %(circuit_breaker_closed_window_size)s,
            %(circuit_breaker_half_open_delay)s,
            %(circuit_breaker_half_open_failure_rate_threshold)s,
            %(circuit_breaker_half_open_window_size)s,
            %(circuit_breaker_open_cooldown_period)s,
            %(circuit_breaker_short_circuit_404s_failure_rate_threshold)s,
            %(circuit_breaker_short_circuit_404s_window_size)s,
            %(circuit_breaker_short_circuit_errors_failure_rate_threshold)s,
            %(circuit_breaker_short_circuit_errors_window_size)s,
            %(request_async_session_max_concurrency)s,
            %(request_async_session_retries)s,
            %(request_async_session_timeout)s,
            %(request_athrottle_base_rate)s,
            %(request_athrottle_burn_in)s,
            %(request_athrottle_max_rate)s,
            %(request_athrottle_min_rate)s,
            %(request_athrottle_temperature)s,
            %(request_athrottle_window_size)s,
            %(request_generator_batch_size)s,
        )
        """

        # Define the values to be inserted
        params = {
            "project_id": jobdata.project_id,
            "dataset": jobdata.dataset,
            "category_id": jobdata.category_id,
            "category": jobdata.category,
            "job_name": jobdata.job_name,
            "dt_created": jobdata.dt_created,
            "dt_scheduled": jobdata.dt_scheduled,
            "dt_started": jobdata.dt_started,
            "dt_ended": jobdata.dt_ended,
            "max_requests": jobdata.max_requests,
            "batch_size": jobdata.batch_size,
            "bookmark": jobdata.bookmark,
            "runtime": jobdata.runtime,
            "request_count": jobdata.request_count,
            "record_count": jobdata.record_count,
            "request_throughput": jobdata.request_throughput,
            "record_throughput": jobdata.record_throughput,
            "total_errors": jobdata.total_errors,
            "redirect_errors": jobdata.redirect_errors,
            "client_errors": jobdata.client_errors,
            "server_errors": jobdata.server_errors,
            "data_errors": jobdata.data_errors,
            "unknown_errors": jobdata.unknown_errors,
            "page_not_found_errors": jobdata.page_not_found_errors,
            "total_error_rate": jobdata.total_error_rate,
            "redirect_error_rate": jobdata.redirect_error_rate,
            "client_error_rate": jobdata.client_error_rate,
            "server_error_rate": jobdata.server_error_rate,
            "data_error_rate": jobdata.data_error_rate,
            "unknown_error_rate": jobdata.unknown_error_rate,
            "page_not_found_error_rate": jobdata.page_not_found_error_rate,
            "job_status": jobdata.job_status,
            "circuit_breaker_closed_burnin_period": jobdata.circuit_breaker.closed_burnin_period,
            "circuit_breaker_closed_failure_rate_threshold": jobdata.circuit_breaker.closed_failure_rate_threshold,
            "circuit_breaker_closed_window_size": jobdata.circuit_breaker.closed_window_size,
            "circuit_breaker_half_open_delay": jobdata.circuit_breaker.half_open_delay,
            "circuit_breaker_half_open_failure_rate_threshold": jobdata.circuit_breaker.half_open_failure_rate_threshold,
            "circuit_breaker_half_open_window_size": jobdata.circuit_breaker.half_open_window_size,
            "circuit_breaker_open_cooldown_period": jobdata.circuit_breaker.open_cooldown_period,
            "circuit_breaker_short_circuit_404s_failure_rate_threshold": jobdata.circuit_breaker.short_circuit_404s_failure_rate_threshold,
            "circuit_breaker_short_circuit_404s_window_size": jobdata.circuit_breaker.short_circuit_404s_window_size,
            "circuit_breaker_short_circuit_errors_failure_rate_threshold": jobdata.circuit_breaker.short_circuit_errors_failure_rate_threshold,
            "circuit_breaker_short_circuit_errors_window_size": jobdata.circuit_breaker.short_circuit_errors_window_size,
            "request_async_session_max_concurrency": jobdata.async_session.max_concurrency,
            "request_async_session_retries": jobdata.async_session.retries,
            "request_async_session_timeout": jobdata.async_session.timeout,
            "request_athrottle_base_rate": jobdata.async_session.athrottle.base_rate,
            "request_athrottle_burn_in": jobdata.async_session.athrottle.burn_in,
            "request_athrottle_max_rate": jobdata.async_session.athrottle.max_rate,
            "request_athrottle_min_rate": jobdata.async_session.athrottle.min_rate,
            "request_athrottle_temperature": jobdata.async_session.athrottle.temperature,
            "request_athrottle_window_size": jobdata.async_session.athrottle.window_size,
            "request_generator_batch_size": jobdata.request_generator.batch_size,
        }
        with self._database as conn:
            job.job_id = conn.execute(query=query, params=params)
            return job

    def get(self, dataset: Dataset) -> pd.DataFrame:
        """
        Fetches jobs by Dataset.

        Args:
            dataset (Enum[Dataset]): DataSet, either AppData or Review

        Returns:
            pd.DataFrame
        """
        query = """
        SELECT * FROM job where dataset = :dataset;
        """

        params = {"dataset": dataset.value}

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
        params = {"job_id": id}

        # Use the database connection to execute the delete query
        with self._database as conn:
            return conn.execute(query, params)
