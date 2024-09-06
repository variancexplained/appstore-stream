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
# Modified   : Friday September 6th 2024 05:49:32 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #


from appvocai.application.operation.base import Operation
from appvocai.core.enum import OperationType
from appvocai.domain.artifact.request.base import AsyncRequest
from appvocai.domain.artifact.response.response import ResponseAsync
from appvocai.infra.web.asession import AsyncSession


# ------------------------------------------------------------------------------------------------ #
class ExtractOperation(Operation):
    """ """

    __OPERATION_TYPE = OperationType.EXTRACT

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

    async def run(self, async_request: AsyncRequest) -> ResponseAsync:
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
            ResponseAsync: The response from the asynchronous request.

        Raises:
            Exception: If the HTTP request fails or the response validation fails.
        """
        # Stamp the passport as we move through operations customs.
        async_request.passport.operation_type = self.__OPERATION_TYPE
        try:

            # Execute the asynchronous HTTP request
            async_response = await self._session.get(async_request=async_request)

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
