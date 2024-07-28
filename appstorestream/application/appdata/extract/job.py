#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/appdata/extract/job.py                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 02:15:42 am                                                   #
# Modified   : Saturday July 27th 2024 02:41:19 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Union
from uuid import uuid4

from appstorestream.application.appdata.extract.request import \
    AppDataAsyncRequestGen
from appstorestream.application.appdata.extract.response import \
    AppDataAsyncResponse
from appstorestream.application.base.builder import ExtractJobBuilder
from appstorestream.application.base.job import ExtractJob, JobConfig
from appstorestream.core.data import IMMUTABLE_TYPES, DataClass
from appstorestream.core.enum import JobStatus
from appstorestream.infra.repo.appdata import AppDataExtractRepo
from appstorestream.infra.web.asession import ASessionAppData


# ------------------------------------------------------------------------------------------------ #
#                                APP DATA REQUEST CONFIG                                           #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class AppDataRequestConfig(JobConfig):
    """Encapsulates AppData Request Configuration"""
    max_requests: int = sys.maxsize
    batch_size : int = 100

# ------------------------------------------------------------------------------------------------ #
#                                     ASESSION  CONFIG                                             #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class AsessionConfig(JobConfig):
    max_concurrency: int = 10
    retries: int = 3
    timeout: int = 10
# ------------------------------------------------------------------------------------------------ #
#                               ATHROTTLE  CONFIG                                                  #
# ------------------------------------------------------------------------------------------------ #

@dataclass
class AThrottleConfig(JobConfig):
    request_rate: float = 1.0
    burnin_period: int = 50
    burnin_reset: int = 1000
    burnin_rate: float = 1
    burnin_threshold_factor: float = 2
    rolling_window_size: int = 25
    cooldown_factor: float = 2
    cooldown_phase: int = 25
    tolerance: float = 0.8

# ------------------------------------------------------------------------------------------------ #
#                                   APP DATA JOB CONFIG                                            #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class AppDataExtractJobConfig(JobConfig):
    appdata_request_config: AppDataRequestConfig = AppDataRequestConfig()
    asession_config: AsessionConfig = AsessionConfig()
    athrottle_config: AThrottleConfig = AThrottleConfig()
# ------------------------------------------------------------------------------------------------ #
#                                    APPDATA EXTRACT JOB                                           #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class AppDataExtractJob(DataClass):

    @abstractmethod
    def run(self, category_id: int) -> None:
        """Executes the Job."""
        self.category_id=category_id
        for request in self._request_generator():
            response = self._asession.get(request=request)
            response = AppDataAsyncResponse(response=response)
            response.parse_response()
            self._repo.insert(data=response.content)

