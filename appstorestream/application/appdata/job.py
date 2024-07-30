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
# Modified   : Monday July 29th 2024 11:33:56 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from dependency_injector.wiring import Provide, inject

from appstorestream.application.base.job import Job, JobMeta
from appstorestream.application.base.project import Project
from appstorestream.container import AppStoreStreamContainer
from appstorestream.core.enum import JobStatus
from appstorestream.core.service import NestedNamespace
from appstorestream.domain.appdata.request import AppDataAsyncRequestGen, AppDataRequest
from appstorestream.domain.appdata.response import AppDataAsyncResponse
from appstorestream.domain.base.state import CircuitBreaker
from appstorestream.infra.monitor.metrics import Metrics
from appstorestream.infra.repo.appdata import AppDataRepo
from appstorestream.infra.web.asession import ASessionAppData


# ------------------------------------------------------------------------------------------------ #
#                                    APPDATA JOB                                                   #
# ------------------------------------------------------------------------------------------------ #
class AppDataJob(Job):
    """
    Represents a job for handling app data collection.

    This class extends the base `Job` class to manage the specific task of collecting app data. It integrates with various
    repositories and services to execute the job, handle requests, and update project status.

    Attributes:
        project (Project): The project associated with this job.
        max_requests (int): Maximum number of requests to be made during the job. Defaults to `sys.maxsize`.
        batch_size (int): Number of items to process in a single batch. Defaults to 100.
        request_gen_cls (type[AppDataAsyncRequestGen]): Class used to generate requests asynchronously. Defaults to `AppDataAsyncRequestGen`.
        appdata_repo (AppDataRepo): Repository for handling app data persistence. Defaults to `Provide[AppStoreStreamContainer.data.appdata_repo]`.
        asession (ASessionAppData): Asynchronous session for making requests. Defaults to `Provide[AppStoreStreamContainer.web.asession_appdata]`.
        circuit_breaker (CircuitBreaker): Circuit breaker for managing request failures. Defaults to `Provide[AppStoreStreamContainer.state.circuit_breaker]`.

        Args:
            project (Project): The project associated with this job.
            max_requests (int, optional): Maximum number of requests to be made. Defaults to `sys.maxsize`.
            batch_size (int, optional): Number of items to process in each batch. Defaults to 100.
            request_gen_cls (type[AppDataAsyncRequestGen], optional): Class for generating asynchronous requests. Defaults to `AppDataAsyncRequestGen`.
            appdata_repo (AppDataRepo, optional): Repository for app data persistence. Defaults to `Provide[AppStoreStreamContainer.data.appdata_repo]`.
            asession (ASessionAppData, optional): Asynchronous session for requests. Defaults to `Provide[AppStoreStreamContainer.web.asession_appdata]`.
            circuit_breaker (CircuitBreaker, optional): Circuit breaker for managing request failures. Defaults to `Provide[AppStoreStreamContainer.state.circuit_breaker]`.
            metrics (Metrics): Class encapsulating metrics monitored by prometheus.
    """

    @inject
    def __init__(
        self,
        project: Project,
        request_gen_cls: type[AppDataAsyncRequestGen] = AppDataAsyncRequestGen,
        appdata_repo: AppDataRepo = Provide[AppStoreStreamContainer.data.appdata_repo],
        asession: ASessionAppData = Provide[
            AppStoreStreamContainer.web.asession_appdata
        ],
        circuit_breaker: CircuitBreaker = Provide[
            AppStoreStreamContainer.state.circuit_breaker
        ],
        metrics: Metrics = Provide[AppStoreStreamContainer.monitor.metrics],
    ) -> None:
        """
        Initializes the AppDataJob with the specified parameters.
        """
        self._project = project
        self._request_gen_cls = request_gen_cls
        self._appdata_repo = appdata_repo
        self._asession = asession
        self._circuit_breaker = circuit_breaker
        self._metrics = metrics

        self._jobmeta = JobMeta(
            project_id=project.project_id,
            dataset=project.dataset,
            category_id=project.category_id,
            category=project.category,
            job_config=self._job_config,
        )
        self._request_gen = request_gen_cls(
            category_id=self._project.category_id,
            max_requests=self._job_config.max_requests,
            batch_size=self._job_config.batch_size,
            start_page=self._project.bookmark,
        )

    @property
    def job_id(self) -> int:
        return self._jobmeta.job_id

    @job_id.setter
    def job_id(self, job_id: int) -> None:
        self._jobmeta.job_id = job_id

    @property
    def bookmark(self) -> int:
        """
        The last page processed.
        """
        return self._jobmeta.bookmark

    @property
    def started(self) -> datetime:
        return self._jobmeta.dt_started

    @property
    def ended(self) -> datetime:
        return self._jobmeta.dt_ended

    @property
    def status(self) -> str:
        return self._jobmeta.job_status

    async def run(self) -> None:
        """
        Executes the job to collect app data.

        This method starts the job, processes requests in batches, and updates the project bookmark. It continues until
        the job status is no longer `JobStatus.IN_PROGRESS`.

        Each request is sent asynchronously, and the responses are persisted to the app data repository. The circuit
        breaker is used to evaluate the responses and handle potential failures.
        """
        self._start_job()

        while self._jobmeta.job_status == JobStatus.IN_PROGRESS:
            for request in self._request_gen:
                # Execute the request and get an AsyncResponse object.
                response = await self._asession.get(request=request)
                # Persist the response if it's ok
                if response.ok:
                    self._appdata_repo.insert(data=response.get_content())
                    self._update_job(request=request, response=response)
                    self._update_metrics(response=response)
                    self._circuit_breaker.evaluate_response(response=response)

    def terminate(self) -> None:
        """
        Terminates the job and performs cleanup.

        This method sets the job metadata status to terminated and performs any necessary wrap-up operations.
        """
        self._jobmeta.terminate()

    def complete(self) -> None:
        """
        Completes the job and performs wrap-up operations.

        This method sets the job metadata status to completed and updates the project and job metadata accordingly.
        """
        self._jobmeta.complete()

    def _start_job(self) -> None:
        """
        Starts the job and initializes the circuit breaker.

        This method sets the job metadata status to started and begins monitoring with the circuit breaker.
        """
        self._jobmeta.start()
        self._circuit_breaker.start(job=self)

    def _update_job(
        self, request: AppDataRequest, response: AppDataAsyncResponse
    ) -> None:
        self._jobmeta.update(request=request, response=response)

    def _update_metrics(self, response: AppDataAsyncResponse) -> None:

        # Set request duration
        self.metrics.duration.inc(response.duration)

        # Progress Metrics
        self._metrics.request_count.inc(response.request_count)
        self._metrics.response_count.inc(response.response_count)
        self._metrics.record_count.inc(response.record_count)

        # Performance Metrics
        self._metrics.requests_per_second.set(response.requests_per_second)
        self._metrics.responses_per_second.set(response.responses_per_second)
        self._metrics.records_per_second.set(response.records_per_second)

        # Error Metrics
        self._metrics.total_errors.inc(response.total_errors)
        self._metrics.client_errors.inc(response.client_errors)
        self._metrics.server_errors.inc(response.server_errors)
        self._metrics.redirect_errors.inc(response.redirect_errors)
        self._metrics.data_errors.inc(response.data_errors)
        self._metrics.unknown_errors.inc(response.unknown_errors)
        self._metrics.page_not_found_errors.inc(response.page_not_found_errors)

        # Error Rates
        self._metrics.total_error_rate.set(response.total_error_rate)
        self._metrics.client_error_rate.set(response.client_error_rate)
        self._metrics.server_error_rate.set(response.server_error_rate)
        self._metrics.redirect_error_rate.set(response.redirect_error_rate)
        self._metrics.data_error_rate.set(response.data_error_rate)
        self._metrics.unknown_error_rate.set(response.unknown_error_rate)
        self._metrics.page_not_found_error_rate.set(response.page_not_found_error_rate)

    def as_dict(self) -> dict:
        """Obtain attributes from sub components into flattened dictionary."""
        jobmeta = self._jobmeta.as_dict()
        rgen = self._request_gen.as_dict()
        asession = self._asession.as_dict()
        circuit = self._circuit_breaker.as_dict()
        jobmeta["request_generator"] = rgen
        jobmeta["asession"] = asession
        jobmeta["circuit_breaker"] = circuit

        return jobmeta

    def as_namespace(self) -> SimpleNamespace:
        """Convert dictionary representation into a simple namespace."""
        return NestedNamespace(self.as_dict())
