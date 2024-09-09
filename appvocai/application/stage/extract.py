#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/stage/extract.py                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 08:46:29 pm                                               #
# Modified   : Sunday September 8th 2024 08:40:35 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from typing import TypeVar

from appvocai.application.stage.base import Stage
from appvocai.core.enum import StageType
from appvocai.domain.artifact.request.base import AsyncRequest
from appvocai.domain.artifact.response.response import AsyncResponse
from appvocai.infra.web.asession import AsyncSession

# ------------------------------------------------------------------------------------------------ #
T = TypeVar("T")


# ------------------------------------------------------------------------------------------------ #
class ExtractStage(Stage):  # type: ignore
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

    @property
    def stage(self) -> StageType:
        return StageType.EXTRACT

    async def run(self, async_request: AsyncRequest) -> AsyncResponse:  # type: ignore
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
        async_request.context.stage = self.stage
        try:

            # Execute the asynchronous HTTP request
            async_response = await self._async_session.get(async_request=async_request)

        except Exception as e:
            # Log or handle the error appropriately
            # Depending on your logging setup, you might log the error or re-raise it
            print(f"An error occurred during task execution: {e}")
            raise

        return async_response
