#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/metrics/extract.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 09:04:54 pm                                               #
# Modified   : Sunday September 1st 2024 12:41:54 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Extract Metrics Module"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from appvocai.domain.metrics.base import Metrics
from appvocai.domain.response.base import ResponseAsync

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
@dataclass
class MetricsExtract(Metrics):
    """
    Class for capturing and computing extract-related metrics.

    This class tracks metrics related to the extraction phase of a task, including the number of requests,
    average latency, speedup, response size, throughput, adapted request rate, and errors.
    """

    requests: int = 0  # Number of requests in the session
    records: int = 0 # Number of records returned in the session
    latency_average: float = 0.0  # Average latency over the session
    speedup: float = 0.0  # Ratio of total latency to duration
    response_size: float = 0.0  # Total response size in bytes for all responses in the session
    throughput: float = 0.0  # Number of requests per second of duration
    session_control_rate: float = 0.0  # The inverse of delay times requests
    session_control_concurrency: float = 0.0 # Concurrency from the session adapter
    errors: int = 0  # Number of errors encountered in the session

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
            self.session_control_concurrency = async_response.session_control.concurrency

        total_latency = 0.0
        for response in async_response.responses:
            self.requests += 1
            if response.status == 200:
                total_latency += response.latency
                self.records += response.n
                self.response_size += int(response.content_length)  # Convert content_length to int if needed
            else:
                self.errors += 1
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
            logger.warning(f"Negative value for latency_average: {self.latency_average}")
        if self.speedup < 0:
            logger.warning(f"Negative value for speedup: {self.speedup}")
        if self.response_size < 0:
            logger.warning(f"Negative value for response_size: {self.response_size}")
        if self.throughput < 0:
            logger.warning(f"Negative value for throughput: {self.throughput}")
        if self.session_control_rate < 0:
            logger.warning(f"Negative value for session_control_rate: {self.session_control_rate}")
        if self.errors < 0:
            logger.warning(f"Negative value for errors: {self.errors}")
        if self.records < 0:
            logger.warning(f"Negative value for records: {self.records}")