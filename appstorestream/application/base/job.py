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
# Modified   : Monday July 29th 2024 12:43:03 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from appstorestream.application.base.request import AsyncRequest
from appstorestream.application.base.response import AsyncResponse
from appstorestream.core.data import DataClass
from appstorestream.core.enum import JobStatus


# ------------------------------------------------------------------------------------------------ #
#                                      JOB CONFIG                                                  #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class JobConfig(DataClass):
    circuit_breaker_closed_burnin_period: int = 300
    circuit_breaker_closed_failure_rate_threshold: float = 0.5
    circuit_breaker_closed_window_size: int = 300
    circuit_breaker_half_open_delay: int = 2
    circuit_breaker_half_open_failure_rate_threshold: float = 0.3
    circuit_breaker_half_open_window_size: int = 600
    circuit_breaker_open_cooldown_period: int = 300
    circuit_breaker_short_circuit_404s_failure_rate_threshold: float = 0.7
    circuit_breaker_short_circuit_404s_window_size: int = 180
    circuit_breaker_short_circuit_errors_failure_rate_threshold: float = 0.9
    circuit_breaker_short_circuit_errors_window_size: int = 180
    request_asession_max_concurrency: int = 100
    request_asession_retries: int = 3
    request_asession_timeout: int = 30
    request_athrottle_base_rate: int = 5
    request_athrottle_burn_in: int = 10
    request_athrottle_max_rate: int = 100
    request_athrottle_min_rate: int = 1
    request_athrottle_temperature: float = 0.5
    request_athrottle_window_size: int = 10
    request_generator_batch_size: int = 100


# ------------------------------------------------------------------------------------------------ #
#                                       JOB META                                                   #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class JobMeta(DataClass):
    project_id: int
    dataset: str
    category_id: int
    category :str
    job_config: JobConfig
    job_id: int = None
    job_name :str  = None
    dt_created :datetime  = None
    dt_scheduled :datetime  = None
    dt_started :datetime  = None
    dt_ended :datetime  = None
    max_requests: int = sys.maxsize
    batch_size: int = 100
    bookmark :int = 0
    runtime :int = 0
    concurrent_requests_duration: int = 0
    request_count :int = 0
    response_count: int = 0
    record_count :int = 0
    request_throughput :float = 0.0
    response_throughput :float = 0.0
    record_throughput :float = 0.0
    total_errors :int = 0
    redirect_errors: int = 0
    client_errors :int = 0
    server_errors :int = 0
    data_errors :int = 0
    unknown_errors :int = 0
    page_not_found_errors: int = 0
    total_error_rate	: float = 0.0
    redirect_error_rate	: float = 0.0
    client_error_rate	: float = 0.0
    server_error_rate	: float = 0.0
    data_error_rate	: float = 0.0
    unknown_error_rate	: float = 0.0
    page_not_found_error_rate	: float = 0.0
    job_status: str = JobStatus.CREATED.value

    def __post_init__(self) -> None:
        self.job_name = self.job_name or f"{self.dataset} - {self.category_id}: {self.category} - {datetime.now().strftime('%Y-%m-%d, %H:%M:%S')}"
        self.dt_created = self.dt_created or datetime.now()

    def start(self) -> None:
        self.dt_started = datetime.now()
        self.job_status = JobStatus.IN_PROGRESS

    def complete(self) -> None:
        self.job_status = JobStatus.COMPLETE
        self._finalize()

    def cancel(self) -> None:
        self.job_status = JobStatus.CANCELLED
        self._finalize()

    def terminate(self) -> None:
        self.job_status = JobStatus.TERMINATED
        self._finalize()

    def update(self, request: AsyncRequest, response: AsyncRequest) -> None:
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
        self.dt_ended = datetime.now()
        self.runtime = (self.dt_ended-self.dt_started).total_seconds()

        self.request_throughput = self.request_count / self.concurrent_requests_duration
        self.response_throughput = self.response_count / self.concurrent_requests_duration
        self.record_throughput = self.record_count / self.concurrent_requests_duration

        self.total_error_rate = self.total_errors / self.request_count
        self.redirect_error_rate = self.redirect_errors / self.request_count
        self.client_error_rate = self.client_errors / self.request_count
        self.server_error_rate = self.server_errors / self.request_count
        self.data_error_rate = self.data_errors / self.request_count
        self.unknown_error_rate = self.unknown_errors / self.request_count
        self.page_not_found_error_rate = self.page_not_found_errors / self.request_count

    def as_dict(self) -> dict:
        job_data = super().as_dict()
        del job_data['job_config']
        job_data.update(self.job_config.as_dict())
        return job_data

# ------------------------------------------------------------------------------------------------ #
#                                          JOB                                                     #
# ------------------------------------------------------------------------------------------------ #
class Job(ABC):

    @abstractmethod
    def run(self) -> None:
        """Runs the job"""

    @abstractmethod
    def as_dict(self) -> dict:
        """Returns the Job as a dictionary"""

    @classmethod
    @abstractmethod
    def from_dict(cls, job_data: dict) -> Job:
        """Creates a Job instance from a dictionary."""