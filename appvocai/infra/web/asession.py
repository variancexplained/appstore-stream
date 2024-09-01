#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/web/asession.py                                                     #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 04:42:55 am                                                   #
# Modified   : Sunday September 1st 2024 01:21:30 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import asyncio
import logging
from typing import Generic, TypeVar

import aiohttp

from appvocai.domain.response.base import ResponseAsync
from appvocai.infra.base.config import Config
from appvocai.infra.base.service import InfraService
from appvocai.infra.web.adapter import Adapter
from appvocai.infra.web.profile import SessionHistory, SessionProfile

# ------------------------------------------------------------------------------------------------ #
CUSTOM_CLIENT_ERROR_RETURN_CODE = 400
CUSTOM_EXCEPTION_RETURN_CODE = 499

# ------------------------------------------------------------------------------------------------ #
T = TypeVar('T')
# ------------------------------------------------------------------------------------------------ #
#                                         ASESSION                                                 #
# ------------------------------------------------------------------------------------------------ #
class ASession(InfraService):
    """Base class for asynchronous HTTP sessions and requests

    Args:
        throttle (AThrottle): Throttling mechanism to control request rate.
        max_concurrency (int): Maximum number of concurrent requests.
        retries (int): Number of retries if a request fails.
        timeout (int): Timeout for requests in seconds.
        config_cls (type[Config]): Class containing proxy server configurations.
    """

    def __init__(
        self,
        adapter: Adapter,
        history: SessionHistory,
        retries: int = 3,
        timeout: int = 30,
        concurrency: int = 50,
        config_cls: type[Config] = Config,
    ) -> None:
        self._adapter = adapter
        self._history = history
        self._retries = retries
        self._timeout = timeout
        self._timeout_obj = aiohttp.ClientTimeout(total=timeout)
        self._concurrency = concurrency
        self._config = config_cls()

        self._proxy = self._config.proxy

        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    async def get(self, async_request: T) -> ResponseAsync:
        """Formats and executes asynchronous get commands.

        Args:
            request (AsyncRequest): An Asyncronous HTTP Request
        """
        await asyncio.sleep(0.01) # Simulating network delay
        return ResponseAsync()