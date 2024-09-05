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
# Modified   : Thursday September 5th 2024 06:58:10 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import asyncio
import logging
from typing import List, Optional

import aiohttp

from appvocai.application.metrics.extract import MetricsASession
from appvocai.domain.openty.request.base import Request, RequestAsync
from appvocai.domain.openty.response.response import Response, ResponseAsync
from appvocai.infra.base.config import Config
from appvocai.infra.operator.error.metrics import MetricsError
from appvocai.infra.web.adapter import Adapter
from appvocai.infra.web.header import BrowserHeaders
from appvocai.infra.web.profile import SessionProfile

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------ #
#                                   EXTRACTOR                                                      #
# ------------------------------------------------------------------------------------------------ #
class ASession:
    """
    Manages asynchronous HTTP requests and processes them using configured adapters and observers.

    This class handles the creation and management of `aiohttp.ClientSession` objects, manages request retries,
    logs errors, and notifies observers with metrics related to the extraction process.

    Args:
        connector (aiohttp.TCPConnector): The TCP connector to use for the session.
        timeout (aiohttp.ClientTimeout): The timeout settings for the session.
        cookie_jar (aiohttp.DummyCookieJar): The cookie jar to use for managing cookies in the session.
        adapter (Adapter): An adapter for handling session control and rate/concurrency adaptation.
        observer (ObserverASessionMetrics): An observer for collecting and reporting task metrics.
        error_observer (ObserverError): An observer for collecting and reporting error metrics.
        config_cls (type[Config], optional): The configuration class to use. Defaults to `Config`.

    Attributes:
        _connector (aiohttp.TCPConnector): Stores the provided TCP connector.
        _timeout (aiohttp.ClientTimeout): Stores the provided timeout settings.
        _cookie_jar (aiohttp.DummyCookieJar): Stores the provided cookie jar.
        _adapter (Adapter): Stores the provided adapter for session control.
        _observer (ObserverASessionMetrics): Stores the provided observer for task metrics.
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
            total=self._config.asession.timeout
        )
        self._cookie_jar = cookie_jar
        self._adapter = adapter
        self._observer = observer
        self._error_observer = error_observer

        self._session_request_limit: int = self._config.asession.session_request_limit
        self._retries: int = self._config.asession.retries
        self._concurrency: int = self._config.asession.concurrency
        self._proxies = self._config.proxy

        self._session_request_count: int = 0
        self._session_active = False
        self._session: Optional[aiohttp.ClientSession] = None
        self._headers: BrowserHeaders = BrowserHeaders()

        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def __enter__(self) -> None:
        """Creates and initializes the aiohttp client session."""
        await self._create_session()

    async def __exit__(self) -> None:
        """Closes the aiohttp client session."""
        if self._session:
            await self._session.close()
            self._session_active = False

    async def get(self, async_request: RequestAsync[Request]) -> ResponseAsync:
        """
        Executes asynchronous HTTP GET requests, processes the responses, and returns them.

        Args:
            async_request (RequestAsync[Request]): The asynchronous request object containing individual requests.

        Returns:
            ResponseAsync: The response object containing the individual responses and related metadata.
        """
        profile = self._create_profile(async_request=async_request)
        self._session_request_count += async_request.n
        semaphore = asyncio.Semaphore(self._concurrency)
        tasks = [
            self.make_request(request, semaphore) for request in async_request.requests
        ]

        profile.send()
        responses = await asyncio.gather(*tasks)
        profile.recv()
        profile = self._update_profile(profile=profile, responses=responses)
        self._adapter.adapt_requests(profile=profile)
        delay = self._adapter.session_control.delay
        await asyncio.sleep(delay)

        self._concurrency = int(self._adapter.session_control.concurrency)
        response = ResponseAsync(
            request_count=async_request.n,
            response_count=len(responses),
            session_control=self._adapter.session_control,
            responses=responses,
        )

        if self._reset_session_if_expired():
            await self._create_session()

        metrics = MetricsASession()
        metrics.compute(async_response=response)
        self._observer.notify(metrics=metrics)

        return response

    def _create_profile(self, async_request: RequestAsync[Request]) -> SessionProfile:
        """
        Creates a session profile for tracking request and response metrics.

        Args:
            async_request (RequestAsync[Request]): The asynchronous request object.

        Returns:
            SessionProfile: The profile object for tracking session metrics.
        """
        profile = SessionProfile()
        profile.requests = async_request.n
        return profile

    def _update_profile(
        self, profile: SessionProfile, responses: List[Response]
    ) -> SessionProfile:
        """
        Updates the session profile with response metrics.

        Args:
            profile (SessionProfile): The session profile object.
            responses (List[Response]): The list of response objects.

        Returns:
            SessionProfile: The updated session profile.
        """
        profile.responses = len(responses)
        for response in responses:
            profile.add_latency(response.latency)
        return profile

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
        response = Response()
        headers = request.headers or next(self._headers)

        async with semaphore:
            while response.retries < self._retries:
                try:
                    response.parse_request(request=request)
                    if self._session:
                        async with self._session.get(
                            headers=headers,
                            url=request.baseurl,
                            proxy=self._proxies,
                            params=request.params,
                        ) as resp:
                            resp.raise_for_status()
                            await response.parse_response(response=resp)
                            return response
                    else:
                        msg = "Session object is None"
                        self._logger.exception(msg)
                        raise TypeError(msg)

                except aiohttp.ClientResponseError as e:
                    if response.retries == self._retries - 1:
                        metrics = MetricsError()
                        metrics.retries += 1
                        metrics.compute(
                            operator=self.__class__.__name__, error_code=e.status
                        )
                        self._error_observer.notify(metrics=metrics)
                    if 400 <= e.status < 500:
                        self._logger.warning(
                            f"ClientResponseError: Response code: {e.status} - {e}. Retry #{metrics.retries}."
                        )

                    elif 500 <= e.status < 600:
                        self._logger.warning(
                            f"ServerResponseError: Response code: {e.status} - {e}. Retry #{metrics.retries}."
                        )
                    else:
                        self._logger.warning(
                            f"UnexpectedResponseError: Response code: {e.status} - {e}. Retry #{metrics.retries}."
                        )

                except aiohttp.ClientError as e:
                    metrics = MetricsError()
                    metrics.retries += 1

                    metrics.compute(operator=self.__class__.__name__, error_code=400)
                    self._error_observer.notify(metrics=metrics)
                    self._logger.warning(f"ClientError: {e}. Retry #{metrics.retries}.")

                except Exception as e:
                    metrics = MetricsError()
                    metrics.retries += 1
                    metrics.compute(operator=self.__class__.__name__, error_code=4000)
                    self._error_observer.notify(metrics=metrics)
                    self._logger.warning(
                        f"Unknown Error: {e}. Retry #{metrics.retries}."
                    )

                finally:
                    response.retries += 1
                    await asyncio.sleep(2**metrics.retries)  # Exponential backoff

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
                    trust_env=self._config.asession.trust_env,
                    raise_for_status=self._config.asession.raise_for_status,
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
