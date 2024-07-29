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
# Modified   : Sunday July 28th 2024 07:29:31 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from appstorestream.application import CATEGORIES
from appstorestream.application.base.request import BatchRequestGen
from appstorestream.core.data import DataClass
from appstorestream.core.enum import Dataset, JobStatus
from appstorestream.domain.repo import DomainLayerRepo


# ------------------------------------------------------------------------------------------------ #
#                                       JOB META                                                   #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class JobMeta(DataClass):
    project_id: int
    dataset: Dataset
    category_id: int
    category :str
    job_id: int = None
    job_name :str  = None
    dt_created :datetime  = None
    dt_scheduled :datetime  = None
    dt_started :datetime  = None
    dt_ended :datetime  = None
    progress :int = 0
    runtime :int = 0
    request_count :int = 0
    app_count :int = 0
    review_count :int = 0
    request_throughput :float = 0.0
    app_throughput :float = 0.0
    review_throughput :float = 0.0
    total_errors :int = 0
    redirect_errors: int = 0
    client_errors :int = 0
    server_errors :int = 0
    data_errors :int = 0
    force_restart: bool = False
    job_status:JobStatus= JobStatus.CREATED

    def __post_init__(self) -> None:
        self.job_name = self.job_name or f"{self.dataset.value} - {self.category_id}: {self.category} - {datetime.now().strftime("%Y-%m-%d, %H:%M:%S")}"
        self.dt_created = self.dt_created or datetime.now()

    def start(self) -> None:
        self.dt_started = datetime.now()
        self.status = JobStatus.IN_PROGRESS

    def complete(self) -> None:
        self.status = JobStatus.COMPLETE
        self._finalize()

    def cancel(self) -> None:
        self.status = JobStatus.CANCELLED
        self._finalize()

    def terminate(self) -> None:
        self.status = JobStatus.TERMINATED
        self._finalize()

    def add_response(self, response) -> None:
        self.progress += response.batch_last_page
        self.request_count += response.response_count
        self.app_count += response.app_count

        self.total_errors += response.total_errors
        self.client_errors += response.client_errors
        self.server_errors += response.server_errors
        self.data_errors += response.data_errors

    def _finalize(self) -> None:
        self.dt_ended = datetime.now()
        self.runtime = (self.dt_ended-self.dt_started).total_seconds()
        self.request_throughput = self.request_count / self.runtime
        self.app_throughput = self.app_count / self.runtime
        self.review_throughput = self.review_count / self.runtime

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

    @abstractmethod
    @classmethod
    def from_dict(cls, job_data: dict) -> Job:
        """Creates a Job instance from a dictionary."""