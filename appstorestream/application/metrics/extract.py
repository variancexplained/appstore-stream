#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/metrics/extract.py                                      #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday August 15th 2024 04:31:15 pm                                               #
# Modified   : Saturday August 17th 2024 03:41:53 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Asynchronous Response Metrics Module"""

import time
from dataclasses import dataclass, field
from typing import Union

import aiohttp
import numpy as np

from appstorestream.application.base.metrics import (
    ExtractMetrics,
    JobMetrics,
    TaskMetrics,
)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ExtractTaskMetrics(ExtractMetrics, TaskMetrics):
    level: str = "task"
    throttle_concurrency_efficiency_ratio: float = 0.0
    throttle_average_latency_efficiency_ratio: float = 0.0
    throttle_total_latency_efficiency_ratio: float = 0.0
    latencies: list[float] = field(default_factory=list)

    def start(self) -> None:
        # Task Start Timestamp
        self.runtime_start_timestamp_seconds = time.time()

    def stop(self) -> None:
        # Stop time
        self.runtime_stop_timestamp_seconds = time.time()
        self.runtime_duration_seconds = (
            self.runtime_stop_timestamp_seconds - self.runtime_start_timestamp_seconds
        )
        self._compute_request_metrics()
        self._compute_response_metrics()
        self._compute_success_failure_rates()
        self._compute_throttle_metrics()

    def add_latency(self, latency: float) -> None:
        self.latencies.append(latency)

    def add_response(self, response: aiohttp.ClientResponse) -> None:
        self.response_size_bytes_total += response.content_length
        self.response_count_total += 1

    def log_http_error(self, return_code: int) -> None:
        self.success_failure_errors_total += 1
        if 300 <= return_code <= 399:
            self.success_failure_redirect_errors_total += 1
        elif 400 <= return_code <= 499:
            self.success_failure_client_errors_total += 1
        elif 500 <= return_code <= 599:
            self.success_failure_server_errors_total += 1
        else:
            self.success_failure_unknown_errors_total += 1

    def _compute_request_metrics(self) -> None:
        # Requests per second
        self.request_per_second_ratio = (
            (self.request_count_total / self.runtime_duration_seconds)
            if self.runtime_duration_seconds > 0
            else 0
        )

    def _compute_response_metrics(self) -> None:
        # Responses per second
        self.response_per_second_ratio = (
            (self.response_count_total / self.runtime_duration_seconds)
            if self.runtime_duration_seconds > 0
            else 0
        )

        # Average Latency
        self.response_average_latency_seconds = np.mean(self.latencies)
        # Total Latency
        self.response_latency_seconds_total = np.sum(self.latencies)
        # Average Response Size
        self.response_average_size_bytes = (
            self.response_size_bytes_total / self.response_count_total
            if self.response_count_total > 0
            else 0
        )

    def _compute_success_failure_rates(self) -> None:
        self.success_failure_request_failure_rate_ratio = (
            (self.success_failure_errors_total / self.request_count_total)
            if self.request_count_total > 0
            else 0
        )

        self.success_failure_request_success_rate_ratio = (
            1 - self.success_failure_request_failure_rate_ratio
        )

    def _compute_throttle_metrics(self) -> None:
        # Concurrency Efficiency
        self.throttle_concurrency_efficiency_ratio = (
            (
                self.response_average_latency_seconds
                / self.runtime_duration_seconds
                / self.request_count_total
            )
            if self.runtime_duration_seconds > 0
            else 0
        )

        # Average latency efficiency
        self.throttle_average_latency_efficiency_ratio = (
            (self.response_average_latency_seconds / self.runtime_duration_seconds)
            if self.runtime_duration_seconds > 0
            else 0
        )

        # Total latency Efficiency
        self.throttle_total_latency_efficiency_ratio = (
            (self.response_latency_seconds_total / self.runtime_duration_seconds)
            if self.runtime_duration_seconds > 0
            else 0
        )


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ExtractJobMetrics(JobMetrics, ExtractMetrics):
    level: str = "job"
    session_count_total: int = 0

    def update_metrics(self, task_metrics: Union[TaskMetrics, ExtractMetrics]) -> None:
        self._update_runtime_metrics(task_metrics=task_metrics)
        self._update_request_metrics(task_metrics=task_metrics)
        self._update_response_metrics(task_metrics=task_metrics)
        self._update_success_failure_metrics(task_metrics=task_metrics)

    def _update_runtime_metrics(
        self, task_metrics: Union[TaskMetrics, ExtractMetrics]
    ) -> None:
        # Sets runtime start timestamp if not already set.
        self.runtime_start_timestamp_seconds = (
            self.runtime_start_timestamp_seconds
            or task_metrics.runtime_start_timestamp_seconds
        )
        # Sets runtime stop to task stop in case of job failure, we
        # have the most recent timestamp
        self.runtime_stop_timestamp_seconds = (
            task_metrics.runtime_stop_timestamp_seconds
        )
        # Increment job duration
        self.runtime_duration_seconds_total += task_metrics.runtime_duration_seconds

    def _update_request_metrics(
        self, task_metrics: Union[TaskMetrics, ExtractMetrics]
    ) -> None:
        # Session count
        self.request_session_count_total += 1
        # Request Count
        self.request_count_total += task_metrics.request_count_total
        # Requests per Second
        self.request_per_second_ratio = (
            self.request_count_total / self.runtime_duration_seconds_total
        )

    def _update_response_metrics(
        self, task_metrics: Union[TaskMetrics, ExtractMetrics]
    ) -> None:
        # Response Count
        self.response_count_total += task_metrics.response_count_total
        # Responses per Second
        self.response_per_second_ratio = (
            self.response_count_total / self.runtime_duration_seconds_total
        )

        # Total Latency
        self.response_latency_seconds_total += (
            task_metrics.response_latency_seconds_total
        )
        # Average Latency
        self.response_average_latency_seconds = (
            self.response_latency_seconds_total / self.response_count_total
        )

        # Total Size of Responses
        self.response_size_bytes_total += task_metrics.response_size_bytes_total
        # Average response size
        self.response_average_size_bytes = (
            self.response_size_bytes_total / self.response_count_total
        )

    def _update_success_failure_metrics(
        self, task_metrics: Union[TaskMetrics, ExtractMetrics]
    ) -> None:
        # Retries
        self.success_failure_retries_total += task_metrics.success_failure_retries_total
        # Errors
        self.success_failure_errors_total += task_metrics.success_failure_errors_total
        # Client Errors
        self.success_failure_client_errors_total += (
            task_metrics.success_failure_client_errors_total
        )
        # Server Errors
        self.success_failure_server_errors_total += (
            task_metrics.success_failure_server_errors_total
        )
        # Redirect Errors
        self.success_failure_redirect_errors_total += (
            task_metrics.success_failure_redirect_errors_total
        )
        # Unkown Errors
        self.success_failure_unknown_errors_total += (
            task_metrics.success_failure_unknown_errors_total
        )
        # Failure Rate
        self.success_failure_request_failure_rate_ratio = (
            self.success_failure_errors_total / self.request_count_total
        )
        # Success Rate
        self.success_failure_request_success_rate_ratio = (
            1 - self.success_failure_request_failure_rate_ratio
        )
