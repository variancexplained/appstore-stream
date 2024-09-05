#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/task/extract.py                                               #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 08:46:29 pm                                               #
# Modified   : Thursday September 5th 2024 06:58:06 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #


from appvocai.application.metrics.extract import MetricsExtract
from appvocai.application.task.base import Task
from appvocai.domain.request.base import RequestAsync
from appvocai.domain.response.response import ResponseAsync
from appvocai.infra.observer.extract import ObserverASessionMetrics
from appvocai.infra.web.asession import ASession


# ------------------------------------------------------------------------------------------------ #
class TaskExtract(Task):
    """ """

    def __init__(self, asession: ASession, observer: ObserverASessionMetrics) -> None:
        """
        Initializes the TaskExtract class with the specified dependencies.

        Args:
            observer (ObserverExtractMetrics): The observer that will monitor and
                report on metrics.
            session (ASession): The session object for performing asynchronous HTTP requests.
            history (SessionHistory): The session history for tracking past requests.
            adapter (Adapter): The adapter for managing session behavior.

        Raises:
            ValueError: If any of the required dependencies are not provided or invalid.
        """
        if not observer or not session or not history or not adapter:
            raise ValueError(
                "All dependencies (observer, session, history, adapter) must be provided."
            )

        self._observer = observer
        self._session = session
        self._history = history
        self._adapter = adapter

    async def run(self, async_request: RequestAsync) -> ResponseAsync:
        """
        Executes the asynchronous task.

        This method performs the following steps:
        1. Collects pre-execution metrics.
        2. Executes an asynchronous HTTP request using the session.
        3. Validates the HTTP response.
        4. Computes and finalizes metrics based on the response.
        5. Notifies the observer of the computed metrics.

        Args:
            async_request (RequestAsync): The asynchronous request to be executed.

        Returns:
            ResponseAsync: The response from the asynchronous request.

        Raises:
            Exception: If the HTTP request fails or the response validation fails.
        """
        metrics = MetricsExtract()

        try:
            # Collect pre-execution metrics
            metrics.pre()

            # Execute the asynchronous HTTP request
            async_response = await self._session.get(async_request=async_request)

            # Collect post-execution metrics
            metrics.post()

            # Validate the response
            async_response.validate()

        except Exception as e:
            # Log or handle the error appropriately
            # Depending on your logging setup, you might log the error or re-raise it
            print(f"An error occurred during task execution: {e}")
            raise

        # Compute and finalize metrics
        metrics.compute(async_response=async_response)
        metrics.validate()

        # Notify the observer with the finalized metrics
        self._observer.notify(metrics=metrics)

        return async_response
