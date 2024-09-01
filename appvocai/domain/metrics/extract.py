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
# Modified   : Sunday September 1st 2024 02:34:02 am                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone

from appvocai.domain.metrics.base import Metrics
from appvocai.domain.response.base import ResponseAsync


# ------------------------------------------------------------------------------------------------ #
@dataclass

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
    response_size: float = 0.0  # Total response size in bytes for all responses in the session
    throughput: float = 0.0  # Number of requests per second of duration
    adapted_request_rate: float = 0.0  # The inverse of delay times requests
    errors: int = 0  # Number of errors encountered in the session

    def pre(self) -> None:
        """
        Marks the start time of the extract task.

        This method should be called at the beginning of the extraction process to record
        the current UTC time as the start time of the task.
        """
        self.start = datetime.now(timezone.utc)

    def post(self) -> None:
        """
        Marks the end time of the extract task and computes its duration.

        This method should be called at the end of the extraction process to record the current
        UTC time as the end time. It also computes the task's duration by calculating the
        difference between the end and start times.
        """
        self.end = datetime.now(timezone.utc)
        if isinstance(self.start, datetime):
            self.duration = (self.end - self.start).total_seconds()

    @abstractmethod
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
        self.adapted_request_rate = async_response.adapted_request_rate
        total_latency = 0.0
        for response in async_response.responses:
            self.requests += 1
            if response.status == 200:
                total_latency += response.latency
                self.response_size += int(response.content_length)  # Convert content_length to int if needed
            else:
                self.errors += 1
        self.latency_average = total_latency / self.requests if self.requests > 0 else 0
        self.speedup = total_latency / self.duration if self.duration > 0 else 0
        self.throughput = self.requests / self.duration if self.duration > 0 else 0
