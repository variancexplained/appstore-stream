#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/base/job.py                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 02:15:42 am                                                   #
# Modified   : Monday July 29th 2024 02:50:39 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Job Module"""
from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from appstorestream.application.base.service import AppService
from appstorestream.core.data import DataClass
from appstorestream.core.enum import JobStatus
from appstorestream.domain.base.request import AsyncRequest
from appstorestream.domain.base.response import AsyncResponse


# ------------------------------------------------------------------------------------------------ #
#                                       JOB META                                                   #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class JobMeta(DataClass):
    """
    A class to hold metadata about a job.

    Attributes:
        project_id (int): The ID of the project.
        dataset (str): The name of the dataset.
        category_id (int): The ID of the category.
        category (str): The name of the category.
        job_id (int, optional): The ID of the job. Defaults to None.
        job_name (str, optional): The name of the job. Defaults to None.
        dt_created (datetime, optional): The creation datetime. Defaults to None.
        dt_scheduled (datetime, optional): The scheduled datetime. Defaults to None.
        dt_started (datetime, optional): The start datetime. Defaults to None.
        dt_ended (datetime, optional): The end datetime. Defaults to None.
        max_requests (int, optional): The maximum number of requests. Defaults to sys.maxsize.
        batch_size (int, optional): The batch size. Defaults to 100.
        bookmark (int, optional): The bookmark. Defaults to 0.
        runtime (int, optional): The runtime duration in seconds. Defaults to 0.
        concurrent_requests_duration (int, optional): The duration of concurrent requests. Defaults to 0.
        request_count (int, optional): The number of requests made. Defaults to 0.
        response_count (int, optional): The number of responses received. Defaults to 0.
        record_count (int, optional): The number of records processed. Defaults to 0.
        request_throughput (float, optional): The request throughput. Defaults to 0.0.
        response_throughput (float, optional): The response throughput. Defaults to 0.0.
        record_throughput (float, optional): The record throughput. Defaults to 0.0.
        total_errors (int, optional): The total number of errors. Defaults to 0.
        redirect_errors (int, optional): The number of redirect errors. Defaults to 0.
        client_errors (int, optional): The number of client errors. Defaults to 0.
        server_errors (int, optional): The number of server errors. Defaults to 0.
        data_errors (int, optional): The number of data errors. Defaults to 0.
        unknown_errors (int, optional): The number of unknown errors. Defaults to 0.
        page_not_found_errors (int, optional): The number of page not found errors. Defaults to 0.
        total_error_rate (float, optional): The total error rate. Defaults to 0.0.
        redirect_error_rate (float, optional): The redirect error rate. Defaults to 0.0.
        client_error_rate (float, optional): The client error rate. Defaults to 0.0.
        server_error_rate (float, optional): The server error rate. Defaults to 0.0.
        data_error_rate (float, optional): The data error rate. Defaults to 0.0.
        unknown_error_rate (float, optional): The unknown error rate. Defaults to 0.0.
        page_not_found_error_rate (float, optional): The page not found error rate. Defaults to 0.0.
        job_status (str, optional): The status of the job. Defaults to JobStatus.CREATED.value.
    """

    project_id: int
    dataset: str
    category_id: int
    category: str
    job_id: int = None
    job_name: str = None
    dt_created: datetime = None
    dt_scheduled: datetime = None
    dt_started: datetime = None
    dt_ended: datetime = None
    max_requests: int = sys.maxsize
    batch_size: int = 100
    bookmark: int = 0
    runtime: int = 0
    concurrent_requests_duration: int = 0
    request_count: int = 0
    response_count: int = 0
    record_count: int = 0
    request_throughput: float = 0.0
    response_throughput: float = 0.0
    record_throughput: float = 0.0
    total_errors: int = 0
    redirect_errors: int = 0
    client_errors: int = 0
    server_errors: int = 0
    data_errors: int = 0
    unknown_errors: int = 0
    page_not_found_errors: int = 0
    total_error_rate: float = 0.0
    redirect_error_rate: float = 0.0
    client_error_rate: float = 0.0
    server_error_rate: float = 0.0
    data_error_rate: float = 0.0
    unknown_error_rate: float = 0.0
    page_not_found_error_rate: float = 0.0
    job_status: str = JobStatus.CREATED.value

    def __post_init__(self) -> None:
        """Initializes the job meta data post object creation."""
        self.job_name = (
            self.job_name
            or f"{self.dataset} - {self.category_id}: {self.category} - {datetime.now().strftime('%Y-%m-%d, %H:%M:%S')}"
        )
        self.dt_created = self.dt_created or datetime.now()

    def start(self) -> None:
        """Marks the job as started."""
        self.dt_started = datetime.now()
        self.job_status = JobStatus.IN_PROGRESS

    def complete(self) -> None:
        """Marks the job as completed."""
        self.job_status = JobStatus.COMPLETE
        self._finalize()

    def cancel(self) -> None:
        """Marks the job as cancelled."""
        self.job_status = JobStatus.CANCELLED
        self._finalize()

    def terminate(self) -> None:
        """Marks the job as terminated."""
        self.job_status = JobStatus.TERMINATED
        self._finalize()

    def update(self, request: AsyncRequest, response: AsyncResponse) -> None:
        """
        Updates the job metadata with the latest request and response details.

        Args:
            request (AsyncRequest): The asynchronous request object.
            response (AsyncResponse): The asynchronous response object.
        """
        self.bookmark = request.bookmark + 1
        self.concurrent_requests_duration += response.concurrent_requests_duration
        self.request_count += response.request_count
        self.response_count += response.response_count
        self.record_count += response.record_count

        self.total_errors += response.total_errors
        self.client_errors += response.client_errors
        self.server_errors += response.server_errors
        self.data_errors += response.data_errors
        self.unknown_errors += response.unknown_errors
        self.page_not_found_errors += response.page_not_found_errors

    def _finalize(self) -> None:
        """Finalizes the job by calculating throughput and error rates."""
        self.dt_ended = datetime.now()
        self.runtime = (self.dt_ended - self.dt_started).total_seconds()

        self.request_throughput = self.request_count / self.concurrent_requests_duration
        self.response_throughput = (
            self.response_count / self.concurrent_requests_duration
        )
        self.record_throughput = self.record_count / self.concurrent_requests_duration

        self.total_error_rate = self.total_errors / self.request_count
        self.redirect_error_rate = self.redirect_errors / self.request_count
        self.client_error_rate = self.client_errors / self.request_count
        self.server_error_rate = self.server_errors / self.request_count
        self.data_error_rate = self.data_errors / self.request_count
        self.unknown_error_rate = self.unknown_errors / self.request_count
        self.page_not_found_error_rate = self.page_not_found_errors / self.request_count

    def as_dict(self) -> dict:
        """
        Converts the job metadata to a dictionary.

        Returns:
            dict: The job metadata as a dictionary.
        """
        job_data = super().as_dict()
        del job_data["job_config"]
        job_data.update(self.job_config.as_dict())
        return job_data


# ------------------------------------------------------------------------------------------------ #
#                                          JOB                                                     #
# ------------------------------------------------------------------------------------------------ #
class Job(AppService):
    """
    An abstract base class for Jobs.

    Methods:
        run(): Runs the job.
        as_dict(): Returns the Job as a dictionary.
    """

    @abstractmethod
    def run(self) -> None:
        """Runs the job"""

    @abstractmethod
    def as_dict(self) -> dict:
        """Returns the Job as a dictionary"""
