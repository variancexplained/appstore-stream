#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/operator/extract/extractor.py                                       #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 04:42:55 am                                                   #
# Modified   : Wednesday September 4th 2024 05:42:54 am                                            #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import asyncio
import logging
from typing import List, Optional

import aiohttp

from appvocai.domain.request.base import Request, RequestAsync
from appvocai.domain.response.response import Response, ResponseAsync
from appvocai.infra.base.config import Config
from appvocai.infra.operator.error.metrics import MetricsError
from appvocai.infra.operator.error.observer import ObserverError
from appvocai.infra.operator.extract.metrics import MetricsExtractor
from appvocai.infra.operator.extract.observer import ObserverExtractorMetrics
from appvocai.infra.web.adapter import Adapter
from appvocai.infra.web.header import BrowserHeaders
from appvocai.infra.web.profile import SessionProfile

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------ #
#                                   EXTRACTOR                                                      #
# ------------------------------------------------------------------------------------------------ #
class Extractor:
    def __init__(
        self,
        connector: aiohttp.TCPConnector,
        timeout: aiohttp.ClientTimeout,
        cookie_jar: aiohttp.DummyCookieJar,
        adapter: Adapter,
        observer: ObserverExtractorMetrics,
        error_observer: ObserverError,
        config_cls: type[Config] = Config,
    ) -> None:

        self._connector: aiohttp.TCPConnector = connector
        self._timeout: aiohttp.ClientTimeout = timeout
        self._cookie_jar = cookie_jar
        self._adapter = adapter
        self._observer = observer
        self._error_observer = error_observer
        self._config: Config = config_cls()

        # Extract primary configuration values
        self._session_request_limit: int = self._config.extractor.session_request_limit
        self._retries: int = self._config.extractor.retries
        self._concurrency: int = self._config.extractor.concurrency
        self._proxies = self._config.proxy

        # Initialize counters,
        self._session_request_count: int = 0
        self._session_active = False
        self._session: Optional[aiohttp.ClientSession] = None
        self._headers: BrowserHeaders = BrowserHeaders()

        self._session_active = False

        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def __enter__(self) -> None:
        await self._create_session()

    async def __exit__(self) -> None:
        if self._session:
            await self._session.close()
            self._session_active = False

    async def get(self, async_request: RequestAsync[Request]) -> ResponseAsync:

        # Create a session profiler to capture stats for rate and concurrency adaptation object
        profile = self._create_profile(async_request=async_request)
        # Increment requests processed by the session and set request count no profile.
        self._session_request_count += async_request.n
        # Update the concurrency Semaphore for the current concurrency value
        semaphore = asyncio.Semaphore(self._concurrency)
        # Create the the asyncio concurrency tasks.
        tasks = [
            self.make_request(request, semaphore) for request in async_request.requests
        ]

        # We wrap the request in a profile send/recv envelope to capture response time.
        profile.send()
        responses = await asyncio.gather(*tasks)
        profile.recv()
        # Update the profile object with latencies and responses
        profile = self._update_profile(profile=profile, responses=responses)
        # Adapt request rate and concurrency to current conditions
        self._adapter.adapt_requests(profile=profile)
        # Execute the auto adapted delay
        delay = self._adapter.session_control.delay
        # Execute the computed delay
        await asyncio.sleep(delay)

        # Set the adapted concurrency
        self._concurrency = int(self._adapter.session_control.concurrency)
        # Create the response object that encapsulates the request transaction
        response = ResponseAsync(
            request_count=async_request.n,
            response_count=len(responses),
            session_control=self._adapter.session_control,
            responses=responses,
        )

        # If the request limit has been exceeded, create a new session.
        if self._reset_session_if_expired():
            await self._create_session()

        # Compute metrics and notify the observer.
        metrics = MetricsExtractor()
        metrics.compute(async_response=response)
        self._observer.notify(metrics=metrics)

        return response

    def _create_profile(self, async_request: RequestAsync[Request]) -> SessionProfile:
        profile = SessionProfile()
        profile.requests = async_request.n
        return profile

    def _update_profile(
        self, profile: SessionProfile, responses: List[Response]
    ) -> SessionProfile:
        profile.responses = len(responses)
        for response in responses:
            profile.add_latency(response.latency)
        return profile

    async def make_request(
        self, request: Request, semaphore: asyncio.Semaphore
    ) -> Optional[Response]:

        # Create a response object and parse information from the request for logging purposes
        response = Response()

        # Obtain headers if not already provided.
        headers = request.headers or next(self._headers)

        async with semaphore:
            while response.retries < self._retries:
                try:
                    # Parsing the request starts the latency clock.
                    response.parse_request(request=request)
                    if self._session:
                        async with self._session.get(
                            headers=headers,
                            url=request.baseurl,
                            proxy=self._proxies,
                            params=request.params,
                        ) as resp:
                            resp.raise_for_status()
                            # Parsing the response stops the latency clock.
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

            # If all retries are exhausted, log and return None
            self._logger.error("Exhausted retries. Returning to calling environment.")
            return None

    async def _create_session(self) -> None:

        attempt = 0

        while attempt < self._retries:

            try:
                self._session = aiohttp.ClientSession(
                    connector=self._connector,
                    timeout=self._timeout,
                    trust_env=self._config.extractor.trust_env,
                    raise_for_status=self._config.extractor.raise_for_status,
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

        # If all retries are exhausted, turn the lights out. We're done.
        msg = "Exhaused retries. Unable to establish an aiohttp.ClientSession."
        self._logger.exception(msg)
        raise RuntimeError(msg)

    async def _reset_session_if_expired(self) -> None:
        """Creates a new session if max requests per session exceeded."""
        if self._session_request_count > self._session_request_limit:
            if self._session_active and self._session:
                await self._session.close()
            await self._create_session()
