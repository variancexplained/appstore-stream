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
# Modified   : Saturday July 27th 2024 02:22:36 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from appstorestream.application.response import AsyncRequestGen
from appstorestream.core.data import IMMUTABLE_TYPES, DataClass
from appstorestream.core.enum import Dataset, JobStatus, Stage


# ------------------------------------------------------------------------------------------------ #
#                                      JOB CONFIG                                                  #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class JobConfig(DataClass):
    """Abstract base class for Job Configuration"""



# ------------------------------------------------------------------------------------------------ #
#                                          JOB                                                     #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class Job(DataClass):
    dataset: Dataset
    stage: Stage
    category_id: int
    category: str
    id: str = str(uuid4())
    name: str = None
    created: datetime = datetime.now()
    scheduled: datetime = None
    started: datetime = None
    ended: datetime = None
    progress: int = 0
    runtime:  int = 0
    request_count: int = 0
    app_count: int = 0
    review_count: int = 0
    request_throughput: float = 0
    app_throughput: float = 0
    total_latency: float = 0
    ave_latency: float = 0
    total_errors: float = 0
    client_errors: float = 0
    server_errors: float = 0
    data_errors: float = 0
    config_id: str = None
    force_restart: bool = False
    status: JobStatus = JobStatus.CREATED

    def start(self) -> None:
        self.started = datetime.now()
        self.status = JobStatus.IN_PROGRESS

    def complete(self) -> None:
        self.status = JobStatus.COMPLETE
        self.completed = datetime.now()
        self.runtime = (self.ended-self.started).total_seconds()

    def cancel(self) -> None:
        self.status = JobStatus.CANCELLED
        self.cancelled = datetime.now()
        self.runtime = (self._cancelled-self._started).total_seconds()

    def fail(self) -> None:
        self.status = JobStatus.FAILED
        self.completed = datetime.now()
        self.runtime = (self.ended-self.started).total_seconds()

    def stats(self) -> None:
        checkpoint = self.ended or datetime.now()
        self.runtime = (checkpoint-self.started.now()).total_seconds()
        self.request_throughput = self.request_count / self.runtime
        self.app_throughput = self.app_count / self.runtime
        self.ave_latency = self.total_latency / self.request_count

    def add_response(self, response) -> None:
        self.progress += response.batch_last_page
        self.request_count += response.response_count
        self.app_count += response.app_count
        self.total_latency += response.total_latency
        self.total_errors += response.total_errors
        self.client_errors += response.client_errors
        self.server_errors += response.server_errors
        self.data_errors += response.data_errors


    @abstractmethod
    def run(self, category_id: int) -> None:
        """Executes the Job."""

