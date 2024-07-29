#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/appdata/extract/builder.py                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 02:15:42 am                                                   #
# Modified   : Sunday July 28th 2024 11:17:05 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Union
from uuid import uuid4

from appstorestream.application.appdata.extract.request import (
    AppDataAsyncRequestGen, AppDataAsyncRequestGenConfig)
from appstorestream.application.appdata.job import AppDataExtractJob
from appstorestream.application.base.builder import JobBuilder
from appstorestream.core.enum import JobStatus
from appstorestream.infra.repo.appdata import (AppDataExtractRepo,
                                               AppDataRepoConfig)
from appstorestream.infra.web.asession import ASession, AsessionConfig
from appstorestream.infra.web.throttle import AThrottleConfig


# ------------------------------------------------------------------------------------------------ #
#                          APP DATA EXTRACT JOB BUILDER                                            #
# ------------------------------------------------------------------------------------------------ #
class AppDataExtractJobBuilder(JobBuilder):

    def __init__(self) -> None:
        super().__init__()
        self._repo = None


    def with_request_generator_config(self, request_generator_config: AppDataAsyncRequestGenConfig) -> AppDataExtractJobBuilder:
        self._request_generator = AppDataAsyncRequestGen(**request_generator_config.as_dict())
        return self

    def with_throttle(self, throttle_config: AThrottleConfig) -> AppDataExtractJobBuilder:
        self._throttle = AThrottleConfig(**throttle_config.as_dict())

    def with_asession_config(self, asession_config: AsessionConfig) -> AppDataExtractJobBuilder:
        self._asession = ASession(throttle=self._throttle,**asession_config.as_dict())
        return self

    def data_repo_config(self, data_repo_config: AppDataRepoConfig) -> AppDataExtractJobBuilder:
        self._repo = AppDataExtractRepo()
        return self

    def job_repo_config(self, job_repo_config: AppDataRepoConfig) -> AppDataExtractJobBuilder:
        self._repo = AppDataExtractRepo()
        return self


    @abstractmethod
    def build(self) -> None:
        """Constructs a Job Object"""
        job = AppDataExtractJob(name=self._name, category_id=self._category_id, request_generator=self._request_generator)
        job.name = self._name
        job.category_id = self._category_id
        job.type = self._type
        job.scheduled = self._scheduled
        job._request_generator
