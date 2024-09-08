#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/operation/extract.py                                          #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 08:46:29 pm                                               #
# Modified   : Saturday September 7th 2024 06:10:13 pm                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from typing import TypeVar

from appvocai.application.operation.base import Operation
from appvocai.application.orchestration.job import Job
from appvocai.application.orchestration.project import Project
from appvocai.application.orchestration.task import Task
from appvocai.core.enum import Category, DataType
from appvocai.domain.artifact.request.base import AsyncRequest
from appvocai.domain.artifact.response.response import AsyncResponse
from appvocai.infra.identity.passport import JobPassport, ProjectPassport, TaskPassport
from appvocai.infra.web.asession import AsyncSession

# ------------------------------------------------------------------------------------------------ #
T = TypeVar("T")

# ------------------------------------------------------------------------------------------------ #
project = Project(category=Category.BOOKS, data_type=DataType.APPDATA)
project_passport = ProjectPassport(
    owner=project, category=Category.BOOKS, data_type=DataType.APPDATA
)
project.passport = project_passport
job = Job(project=project)
job.passport = JobPassport(owner=job, project_passport=project_passport)
task = Task(job_passport=job.passport)
tp = TaskPassport(owner=task, job_passport=job.passport)


# ------------------------------------------------------------------------------------------------ #
class ExtractOperation(Operation):  # type: ignore
    """ """

    def __init__(self, async_session: AsyncSession) -> None:
        """
        Initializes the TaskExtract class with the specified dependencies.

        Args:
            observer (ObserverExtractMetrics): The observer that will monitor and
                report on metrics.
            session (AsyncSession): The session object for performing asynchronous HTTP requests.
            history (SessionHistory): The session history for tracking past requests.
            adapter (Adapter): The adapter for managing session behavior.

        Raises:
            ValueError: If any of the required dependencies are not provided or invalid.
        """
        self._async_session = async_session

    async def run(self, task_passport: TaskPassport, async_request: AsyncRequest) -> T:  # type: ignore
        """
        Executes the asynchronous task.

        This method performs the following steps:
        1. Collects pre-execution metrics.
        2. Executes an asynchronous HTTP request using the session.
        3. Validates the HTTP response.
        4. Computes and finalizes metrics based on the response.
        5. Notifies the observer of the computed metrics.

        Args:
            async_request (AsyncRequest): The asynchronous request to be executed.

        Returns:
            AsyncResponse: The response from the asynchronous request.

        Raises:
            Exception: If the HTTP request fails or the response validation fails.
        """
        async_request = self.check_in(
            task_passport=task_passport, artifact=async_request
        )  # type: ignore

        try:

            # Execute the asynchronous HTTP request
            async_exaction_response = await self._async_session.get(
                async_request=async_request
            )

            # Validate the response
            async_exaction_response.validate()

            # Parse content

        except Exception as e:
            # Log or handle the error appropriately
            # Depending on your logging setup, you might log the error or re-raise it
            print(f"An error occurred during task execution: {e}")
            raise

        return async_exaction_response


eo = ExtractOperation()


# ------------------------------------------------------------------------------------------------ #
#                             APPDATA EXTRACT OPERATION                                            #
# ------------------------------------------------------------------------------------------------ #
class AppDataExtractOperation(ExtractOperation[AsyncResponse]):
    def __init__(self, async_session: AsyncSession) -> None:
        super().__init__(async_session=async_session)

    def check_out(self, response: AsyncResponse) -> AsyncResponse:  # type: ignore
        """Prepares content for the next stage"""
        for exaction in response.exactions:
            exaction.response.content
        for exaction in response.exactions:
            if exaction.response:
                exaction.response.content = exaction.response.content["results"]
        return response


# ------------------------------------------------------------------------------------------------ #
#                            APPREVIEW EXTRACT OPERATION                                           #
# ------------------------------------------------------------------------------------------------ #
class AppReviewExtractOperation(ExtractOperation[AsyncResponse]):
    def __init__(self, async_session: AsyncSession) -> None:
        super().__init__(async_session=async_session)

    def check_out(self, async_exaction_response: AsyncResponse) -> AsyncResponse:
        """Prepares content for the next stage"""
        for exaction in async_exaction_response.exactions:
            exaction.response.content = exaction.response.content["userReviewList"]
        return async_exaction_response
