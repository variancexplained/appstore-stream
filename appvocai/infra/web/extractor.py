#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/web/extractor.py                                                    #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 04:42:55 am                                                   #
# Modified   : Tuesday September 3rd 2024 10:28:33 pm                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import asyncio
import logging
from typing import Optional
from enum import Enum

import aiohttp
from abc import abstractmethod
from dataclasses import dataclass, field


from appvocai.application.metrics.base import Metrics
from appvocai.domain.request.base import RequestAsync
from appvocai.domain.response.response import ResponseAsync
from appvocai.domain.response.response import ResponseAsync, Response
from appvocai.infra.base.config import Config
from appvocai.infra.web.header import BrowserHeaders
from appvocai.infra.web.profile import SessionProfile
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
class ExtractErrorCode(Enum):
    REDIRECT_ERROR = "3xx"
    CLIENT_ERROR = "4xx"
    SERVER_ERROR = "5xx"
    UNKNOWN_ERROR = "6xx+"


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ErrorLog:
    code: int
    description: str
# ------------------------------------------------------------------------------------------------ #
#                                   EXTRACTOR                                                      #
# ------------------------------------------------------------------------------------------------ #
class Extractor():
    def __init__(self, connector: aiohttp.TCPConnector, timeout: aiohttp.ClientTimeout, config_cls: type[Config] = Config) -> None:
        self._config = config_cls()
        self._connector = connector
        self._timeout = timeout
        self._session_request_limit = self._config.session_request_limit
        self._retries = self._config.retries
        self._concurrency = self._config.concurrency

        self._request_count = 0
        self._session = Optional[aiohttp.ClientSession] = None
        self._headers = BrowserHeaders()

        self._session_active

    async def __enter__(self) -> None:

        self._create_session()

    async def __exit__(self) -> None:
        self._session.close()



    async def get(self, async_request: RequestAsync) -> ResponseAsync:

        # Update the number of requests processed by the session.
        self._requests += async_request.n


        concurrency = asyncio.Semaphore(self._concurrency)

        profile = SessionProfile()
        profile.send()

        tasks = [
            self._make_request(request, concurrency) for request in async_request.requests
        ]
        responses = await asyncio.gather(*tasks)
        profile.recv()
        profile.requests = len(async_request.requests)
        profile.latencies = [response.latency for response in responses]
        #TODO: Ensure adapter session control metrics are stored in the async response

        # If the request limit has been reached, create a new session.
        if self._session_requests_limit_exceeded:
            self._create_session()

    @abstractmethod
    async def parse_response(self, response: aiohttp.ClientResponse) -> Response:


    async def make_request(self, request: U, concurrency: asyncio.Semaphore) -> Response:

        # Create a response object and parse information from the request for logging purposes
        response = Response()


        async with concurrency:
            while response.retries < self._retries:
                try:
                    # Parsing the request starts the latency clock.
                    response.parse_request(request=request)
                    resp = self._session.get(headers=request.headers,
                                                 url=request.baseurl,
                                                 proxy=request.proxy,
                                                 params=request.params)
                    resp.raise_for_status()
                    # Parsing the response stops the latency clock.
                    await response.parse_response(response=resp)
                    return response)

                except aiohttp.ClientResponseError as e:
                    if response.retries == self._retries - 1:
                        # TODO: Create Extractor observer to track errors and retries.
                        profile.log_error(return_code=e.status)
                    if 400 <= e.status < 500:
                        self._logger.warning(
                            f"ClientResponseError: Response code: {e.status} - {e}. Retry #{profile.retries}."
                        )

                    elif 500 <= e.status < 600:
                        self._logger.warning(
                            f"ServerResponseError: Response code: {e.status} - {e}. Retry #{profile.retries}."
                        )
                    else:
                        self._logger.warning(
                            f"UnexpectedResponseError: Response code: {e.status} - {e}. Retry #{profile.retries}."
                        )

                except aiohttp.ClientError as e:
                    profile.log_error(return_code=CUSTOM_CLIENT_ERROR_RETURN_CODE)
                    self._logger.warning(f"ClientError: {e}. Retry #{profile.retries}.")

                except Exception as e:
                    profile.log_error(return_code=CUSTOM_EXCEPTION_RETURN_CODE)
                    self._logger.warning(
                        f"Unknown Error: {e}. Retry #{profile.retries}."
                    )

                finally:
                    response.retries += 1
                    await asyncio.sleep(2**profile.retries)  # Exponential backoff

            # If all retries are exhausted, log and return None
            self._logger.error("Exhausted retries. Returning to calling environment.")
            return None



    def _create_session(self) -> None:
        self._request_count = 0
        self._session = aiohttp.ClientSession(
            connector=self._connector,
            timeout=self._timeout,
            trust_env=self._config.trust_env,


            raise_for_status=self._config.raise_for_status
        )

    def _update_request_count(self, async_request: T) -> None:
        self._request_count += len(async_request.requests)

    def _session_requests_limit_exceeded(self) -> bool:
        return self._request_count > self._session_request_limit






# ------------------------------------------------------------------------------------------------ #
@dataclass
class MetricsExtract(Metrics):
    """
    Class for capturing and computing extract-related metrics.

    This class tracks metrics related to the extraction phase of a task, including the number of requests,
    average latency, speedup, response size, throughput, adapted request rate, and errors.
    """

    requests: int = 0  # Number of requests in the session
    latency_average: float = 0.0  # Average latency over the session
    speedup: float = 0.0  # Ratio of total latency to duration
    response_size: float = (
        0.0  # Total response size in bytes for all responses in the session
    )
    throughput: float = 0.0  # Number of requests per second of duration
    session_control_rate: float = 0.0  # The inverse of delay times requests
    session_control_concurrency: float = 0.0  # Concurrency from the session adapter
    errors: list[ErrorLog] = field(default_factory=list)  # List of error logs

    def compute(self, async_response: ResponseAsync) -> None:
        """
        Computes extract-related metrics based on the provided async response.

        This method processes the `ResponseAsync` object to calculate various metrics, including
        the adapted request rate, total latency, average latency, speedup, response size, and throughput.
        The method should be called after the session has completed and all responses are available.

        Args:
            async_response (ResponseAsync): An object containing the details of the asynchronous responses
            collected during the extraction session.
        """
        if async_response.session_control:
            self.session_control_rate = async_response.session_control.rate
            self.session_control_concurrency = (
                async_response.session_control.concurrency
            )

        total_latency = 0.0
        for response in async_response.responses:
            self.requests += 1
            if response.status == 200:
                total_latency += response.latency
                self.response_size += int(
                    response.content_length
                )  # Convert content_length to int if needed
            else:
                self._log_error(error_code=response.status)

        self.latency_average = total_latency / self.requests if self.requests > 0 else 0
        self.speedup = total_latency / self.duration if self.duration > 0 else 0
        self.throughput = self.requests / self.duration if self.duration > 0 else 0

    def validate(self) -> None:
        """
        Validates the metrics data.

        This method is intended to be implemented by subclasses to perform specific validation
        checks on the metrics data. The validation process should include checks for any invalid
        or unexpected values (e.g., negative values where they shouldn't exist) and issue warnings
        or raise errors as appropriate.

        Subclasses should override this method to ensure that all metrics adhere to the expected
        constraints and are safe to use in subsequent calculations or updates.

        Raises:
            ValueError: Subclasses may raise this exception if the validation fails critically.
        """
        if self.requests < 0:
            logger.warning(f"Negative value for requests: {self.requests}")
        if self.latency_average < 0:
            logger.warning(
                f"Negative value for latency_average: {self.latency_average}"
            )
        if self.speedup < 0:
            logger.warning(f"Negative value for speedup: {self.speedup}")
        if self.response_size < 0:
            logger.warning(f"Negative value for response_size: {self.response_size}")
        if self.throughput < 0:
            logger.warning(f"Negative value for throughput: {self.throughput}")
        if self.session_control_rate < 0:
            logger.warning(
                f"Negative value for session_control_rate: {self.session_control_rate}"
            )
        if self.errors < 0:
            logger.warning(f"Negative value for errors: {self.errors}")
        if self.records < 0:
            logger.warning(f"Negative value for records: {self.records}")

    def _log_error(self, error_code: int) -> None:
        if 300 <= error_code <= 399:
            description = ExtractErrorCode.REDIRECT_ERROR.name
        elif 400 <= error_code <= 499:
            description =  ExtractErrorCode.CLIENT_ERROR.name
        elif 500 <= error_code <= 599:
            description =  ExtractErrorCode.SERVER_ERROR.name
        else:
            description =  ExtractErrorCode.UNKNOWN_ERROR.name

        errors = ErrorLog(code=error_code, description=description)
        self.errors.append(errors)


