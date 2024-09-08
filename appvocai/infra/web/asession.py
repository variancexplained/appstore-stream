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
# Modified   : Saturday September 7th 2024 08:51:59 pm                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import asyncio
import logging
from typing import Awaitable, List, Optional

import aiohttp

from appvocai.container import AppVoCAIContainer
from appvocai.domain.artifact.request.base import AsyncRequest, Request
from appvocai.domain.artifact.response.response import AsyncResponse, Response
from appvocai.infra.base.config import Config
from appvocai.infra.identity.passport import OperationPassport
from appvocai.infra.monitor.extract import ExtractMonitorDecorator
from appvocai.infra.web.adapter import Adapter
from appvocai.infra.web.header import BrowserHeaders

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
monitor: ExtractMonitorDecorator = AppVoCAIContainer.monitor.metrics_extract()
log_error = AppVoCAIContainer.monitor.error()


# ------------------------------------------------------------------------------------------------ #
#                                   EXTRACTOR                                                      #
# ------------------------------------------------------------------------------------------------ #
class AsyncSession:
    """
    Manages asynchronous HTTP requests and processes them using configured adapters and observers.

    This class handles the creation and management of `aiohttp.ClientSession` objects, manages request retries,
    logs errors, and notifies observers with metrics related to the extraction process.

    Args:
        connector (aiohttp.TCPConnector): The TCP connector to use for the session.
        timeout (aiohttp.ClientTimeout): The timeout settings for the session.
        cookie_jar (aiohttp.DummyCookieJar): The cookie jar to use for managing cookies in the session.
        adapter (Adapter): An adapter for handling session control and rate/concurrency adaptation.
        observer (ObserverAsyncSessionMetrics): An observer for collecting and reporting task metrics.
        error_observer (ObserverError): An observer for collecting and reporting error metrics.
        config_cls (type[Config], optional): The configuration class to use. Defaults to `Config`.

    Attributes:
        _connector (aiohttp.TCPConnector): Stores the provided TCP connector.
        _timeout (aiohttp.ClientTimeout): Stores the provided timeout settings.
        _cookie_jar (aiohttp.DummyCookieJar): Stores the provided cookie jar.
        _adapter (Adapter): Stores the provided adapter for session control.
        _observer (ObserverAsyncSessionMetrics): Stores the provided observer for task metrics.
        _error_observer (ObserverError): Stores the provided observer for error metrics.
        _config (Config): The extracted configuration instance.
        _session_request_limit (int): Maximum number of requests per session.
        _retries (int): Number of retries allowed per request.
        _concurrency (int): Base concurrency level for the session.
        _proxies (dict): Proxy settings from the configuration.
        _session_request_count (int): Counter for the number of requests processed in the current session.
        _session_active (bool): Indicates whether a session is currently active.
        _session (Optional[aiohttp.ClientSession]): The active aiohttp client session.
        _headers (BrowserHeaders): Iterator for cycling through browser headers.
        _logger (logging.Logger): Logger instance for the class.
    """

    def __init__(
        self,
        connector: aiohttp.TCPConnector,
        cookie_jar: aiohttp.DummyCookieJar,
        adapter: Adapter,
        config_cls: type[Config] = Config,
    ) -> None:
        self._config: Config = config_cls()
        self._connector: aiohttp.TCPConnector = connector
        self._timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(
            total=self._config.async_session.timeout
        )
        self._cookie_jar = cookie_jar
        self._adapter = adapter
        self.monitor = monitor

        self._session_request_limit: int = (
            self._config.async_session.session_request_limit
        )
        self._retries: int = self._config.async_session.retries
        self._concurrency: int = self._config.async_session.concurrency
        self._proxies = self._config.proxy

        self._session_request_count: int = 0
        self._session_active = False
        self._session: Optional[aiohttp.ClientSession] = None
        self._headers: BrowserHeaders = BrowserHeaders()

        self._passport: Optional[OperationPassport] = None

        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def __enter__(self) -> None:
        """Creates and initializes the aiohttp client session."""
        await self._create_session()

    async def __exit__(self) -> None:
        """Closes the aiohttp client session."""
        if self._session:
            await self._session.close()
            self._session_active = False

    @property
    def passport(self) -> Optional[OperationPassport]:
        return self._passport

    async def get(self, async_request: AsyncRequest[Request]) -> AsyncResponse:
        """
        Executes asynchronous HTTP GET requests, processes the responses, and returns them.

        Args:
            async_request (AsyncRequest[Request]): The asynchronous request object containing individual requests.

        Returns:
            AsyncResponse: The response object containing the individual responses and related metadata.
        """
        # Create a passport for this operation
        self._passport = async_request.passport.creator

        # Initialize the adapter for automatic rate limiting and concurrency throttling
        self._adapter.initialize(async_request=async_request)
        # Create a semaphore with the current concurrency value.
        semaphore = asyncio.Semaphore(self._concurrency)
        # Assemble the async tasks from the requests
        tasks = [
            self.make_request(request, semaphore) for request in async_request.requests
        ]
        # Make the requests
        responses = await self._make_async_request(tasks)
        # Execute rate and concurrency adaption
        await self._adapt_rate_concurrency(responses=responses)

        # Package the responses for the trip back
        async_response = AsyncResponse(operation_passport=self._passport)
        async_response.add_responses(responses=responses)

        # Increment the number of requests processed. The seesion
        # will be recreated once a threshold of requests is reached.
        self._session_request_count += async_request.request_count

        # Check if time to rotate / reset sessions
        if self._reset_session_if_expired():
            await self._create_session()

        return async_response

    @monitor.operation
    async def _make_async_request(
        self, tasks: List[Awaitable[Response]]
    ) -> List[Response]:

        # Wrap the async request between the send and recv timestamps
        self._adapter.profile.send()
        # Await the response transactions (or exactions)
        responses = await asyncio.gather(*tasks)
        # Once compiled, stop the clock with the recv method
        self._adapter.profile.recv()
        return responses

    async def _adapt_rate_concurrency(self, responses: List[Response]) -> None:
        """Compute rate and concurrency for current conditions based on latency."""
        # Update the metrics in the adapter
        self._adapter.update_profile(responses=responses)
        # Compute new request rate and concurrency
        self._adapter.adapt_requests()
        # Obtain the delay from the session control property and invoke async sleep
        delay = self._adapter.session_control.delay
        await asyncio.sleep(delay)
        # Set the concurrency for the next request
        self._concurrency = int(self._adapter.session_control.concurrency)

    @log_error
    @monitor.event
    async def make_request(
        self, request: Request, semaphore: asyncio.Semaphore
    ) -> Optional[Response]:
        """
        Makes an individual HTTP GET request and processes the response.

        Args:
            request (Request): The request object containing the request details.
            semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests.

        Returns:
            Optional[Response]: The response object if the request is successful; None if all retries are exhausted.
        """

        headers = request.headers or next(self._headers)
        attempts = 0

        async with semaphore:
            while attempts < self._retries:
                try:

                    # Make the request.
                    if self._session:
                        async with self._session.get(
                            headers=headers,
                            url=request.baseurl,
                            proxy=self._proxies,
                            params=request.params,
                        ) as resp:
                            resp.raise_for_status()
                            # Instantiate a Response object to capture the HTTP response.
                            if self.passport:
                                response = Response(operation_passport=self.passport)
                            else:
                                msg = "The passport is None. Expected type OperationPassport."
                                self._logger.exception(msg)
                                raise RuntimeError(msg)
                            await response.parse_response(response=resp)
                            return response

                    else:
                        msg = "Session object is None"
                        self._logger.exception(msg)
                        raise TypeError(msg)

                except Exception:
                    attempts += 1
                    await asyncio.sleep(2**attempts)  # Exponential backoff

            self._logger.error("Exhausted retries. Returning to calling environment.")
            return None

    async def _create_session(self) -> None:
        """
        Creates a new aiohttp.ClientSession with the provided settings.

        If session creation fails, it will retry according to the configured retry policy.

        Raises:
            RuntimeError: If the session could not be established after all retries.
        """
        attempt = 0

        while attempt < self._retries:
            try:
                self._session = aiohttp.ClientSession(
                    connector=self._connector,
                    timeout=self._timeout,
                    trust_env=self._config.async_session.trust_env,
                    raise_for_status=self._config.async_session.raise_for_status,
                    cookie_jar=self._cookie_jar,
                )
                self._session_request_count = 0
                self._session_active = True
                break
            except aiohttp.ClientError as e:
                attempt += 1
                msg = f"Attempt to create an aiohttp.ClientSession failed.\n{e}\nRetry #: {attempt}"
                self._logger.warning(msg)
                await asyncio.sleep(2**self._retries)  # Exponential backoff
            except Exception as e:
                attempt += 1
                msg = f"Attempt to create an aiohttp.ClientSession failed.\n{e}\nRetry #: {attempt}"
                self._logger.warning(msg)
                await asyncio.sleep(2**self._retries)  # Exponential backoff

        msg = "Exhausted retries. Unable to establish an aiohttp.ClientSession."
        self._logger.exception(msg)
        raise RuntimeError(msg)

    async def _reset_session_if_expired(self) -> bool:
        """
        Checks if the session request limit has been exceeded and resets the session if necessary.

        Returns:
            bool: True if the session was reset, False otherwise.
        """
        if self._session_request_count > self._session_request_limit:
            if self._session_active and self._session:
                await self._session.close()
            await self._create_session()
            return True
        return False
