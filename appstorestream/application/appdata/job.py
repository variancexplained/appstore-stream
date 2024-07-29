#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/appdata/job.py                                          #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 02:15:42 am                                                   #
# Modified   : Sunday July 28th 2024 04:04:04 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass

from dependency_injector.wiring import inject, Provide

from appstorestream.application.appdata.request import \
    AppDataAsyncRequestGen
from appstorestream.application.appdata.response import \
    AppDataAsyncResponse
from appstorestream.core.enum import JobStatus
from appstorestream.application.base.project import Project
from appstorestream.infra.repo.appdata import AppDataRepo
from appstorestream.infra.web.asession import ASessionAppData
from appstorestream.application.base.job import Job, JobMeta
from appstorestream.container import AppStoreStreamContainer
# ------------------------------------------------------------------------------------------------ #
#                                    APPDATA JOB                                                   #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class AppDataJob(Job):

    def __init__(self,
                 project: Project,
                 max_requests: int = sys.maxsize,
                 batch_size: int = 100,
                 page_not_found_threshold: int = 5,
                 request_gen_cls: type[AppDataAsyncRequestGen] = AppDataAsyncRequestGen,
                 appdata_repo:  AppDataRepo = Provide[AppStoreStreamContainer.data.appdata_repo],
                 project_repo:  AppDataRepo = Provide[AppStoreStreamContainer.data.project_repo],
                 asession: ASessionAppData = Provide[AppStoreStreamContainer.web.asession_appdata],
                 )
        self._project = project
        self._max_requests = max_requests
        self._batch_size = batch_size
        self._page_not_found_threshold = page_not_found_threshold
        self._request_gen_cls = request_gen_cls
        self._appdata_repo = appdata_repo
        self._project_repo = project_repo
        self._asession = asession

        self._pages_not_found = 0


        self._jobmeta = JobMeta(project_id=project.project_id, dataset=project.dataset, category_id=project.category_id, category=project.category)
        self._request_gen = request_gen_cls(max_requests=self._max_requests, batch_size=self._batch_size, start_page=self._project.progress+1)


    @abstractmethod
    async def run(self) -> None:
        """Executes the Job."""

        self._jobmeta.start()

        while self._pages_not_found < self._page_not_found_threshold:

            for request in self._request_gen:
                response = self._asession.get(request=request)
                response = AppDataAsyncResponse(response=response)
                response.parse_response()
                self._appdata_repo.insert(data=response.get_content())
                self._project.progress += response.result_count
                self._pages_not_found += response.page_not_found_errors

            self._jobmeta.complete()


