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
# Modified   : Tuesday September 3rd 2024 07:51:54 pm                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #


from appvocai.infra.base.config import Config
from appvocai.application.task.base import Task
from appvocai.infra.web.metrics import MetricsExtract
from appvocai.domain.request.base import RequestAsync
from appvocai.domain.response.response import ResponseAsync
from appvocai.infra.web.extractor import ASession
from appvocai.core.data import DataClass

# ------------------------------------------------------------------------------------------------ #
class TaskExtract(Task):
    """
    A base class for executing asynchronous extract tasks.

    This class handles the execution of asynchronous HTTP requests, metrics collection,
    validation, and observer notification. It is designed to be subclassed for specific
    types of extract tasks.

    Attributes:
        _observer (ObserverExtractMetrics): The observer that monitors and responds to
            changes in metrics.
        _session (ASession): The session object used to perform asynchronous HTTP requests.
        _history (SessionHistory): The history object that tracks session data.
        _adapter (Adapter): The adapter object that manages session behavior.
    """

    def __init__(self, extractor: Extractor) -> None:
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
            raise ValueError("All dependencies (observer, session, history, adapter) must be provided.")

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

# ------------------------------------------------------------------------------------------------ #
class Extractor(DataClass):
    """Encapsulates objects required by the Extact Task object."""
    requestor: Requestor
    session: ASession


# ------------------------------------------------------------------------------------------------ #
class ExtractorBuilder(ABC):
    @
    def __init__(self, config_cls: Config = Config)
