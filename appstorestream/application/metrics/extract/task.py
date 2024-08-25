#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/metrics/extract/task.py                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 17th 2024 11:14:24 am                                               #
# Modified   : Sunday August 25th 2024 12:11:46 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Extract Task Metrics Module"""
import time
from dataclasses import dataclass, field

import aiohttp
import numpy as np

from appstorestream.core.metrics import Metrics


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ExtractMetrics(Metrics):
    extract_job_runtime_start_timestamp_seconds: float = 0.0
    extract_job_runtime_stop_timestamp_seconds: float = 0.0
    extract_job_runtime_response_time_seconds_total: float = 0.0

    extract_job_request_session_count_total: float = 0.0
    extract_job_request_count_total: int = 0

    extract_job_response_count_total: int = 0
    extract_job_response_average_per_second_ratio: float = 0.0
    extract_job_response_average_latency_seconds: float = 0.0
    extract_job_response_latency_seconds_total: float = 0.0
    extract_job_response_average_size_bytes: int = 0
    extract_job_response_size_bytes_total: int = 0

    extract_job_success_failure_retries_total: int = 0
    extract_job_success_failure_errors_total: int = 0
    extract_job_success_failure_request_failure_rate_ratio: float = 0.0
    extract_job_success_failure_request_success_rate_ratio: float = 0.0

    extract_task_runtime_start_timestamp_seconds: float = 0.0
    extract_task_runtime_stop_timestamp_seconds: float = 0.0
    extract_task_runtime_response_time_seconds: float = 0.0

    extract_task_request_count_total: int = 0
    extract_task_request_per_second_ratio: float = 0.0

    extract_task_response_count_total: int = 0
    extract_task_response_per_second_ratio: float = 0.0
    extract_task_response_average_latency_seconds: float = 0.0
    extract_task_response_latency_seconds_total: float = 0.0
    extract_task_response_average_size_bytes: int = 0
    extract_task_response_size_bytes_total: int = 0

    extract_task_success_failure_retries_total: int = 0
    extract_task_success_failure_errors_total: int = 0
    extract_task_success_failure_client_errors_total: int = 0
    extract_task_success_failure_server_errors_total: int = 0
    extract_task_success_failure_redirect_errors_total: int = 0
    extract_task_success_failure_unknown_errors_total: int = 0
    extract_task_success_failure_request_failure_rate_ratio: float = 0.0
    extract_task_success_failure_request_success_rate_ratio: float = 0.0

    extract_task_throttle_concurrency_efficiency_ratio: float = 0.0
    extract_task_throttle_average_latency_efficiency_ratio: float = 0.0
    extract_task_throttle_total_latency_efficiency_ratio: float = 0.0

    latencies: list[float] = field(default_factory=list)

    def start(self) -> None:
        # Set Job start time if not already set.
        self.extract_job_runtime_start_timestamp_seconds = (
            self.extract_job_runtime_start_timestamp_seconds or time.time()
        )
        # Set task start time.
        self.extract_task_runtime_start_timestamp_seconds = time.time()

    def stop(self) -> None:
        self.extract_job_runtime_stop_timestamp_seconds = time.time()
        self.extract_task_runtime_stop_timestamp_seconds = time.time()
        self.runtime_response_time_seconds = (
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
            (self.request_count_total / self.runtime_response_time_seconds)
            if self.runtime_response_time_seconds > 0
            else 0
        )

    def _compute_response_metrics(self) -> None:
        # Responses per second
        self.response_per_second_ratio = (
            (self.response_count_total / self.runtime_response_time_seconds)
            if self.runtime_response_time_seconds > 0
            else 0
        )

        # Average Latency
        self.response_average_latency_seconds = np.mean(self.latencies)
        # Total Latency
        self.response_latency_seconds_total = np.sum(self.latencies)
        # Response Size
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
                / self.runtime_response_time_seconds
                / self.request_count_total
            )
            if self.runtime_response_time_seconds > 0
            else 0
        )

        # Average latency efficiency
        self.throttle_average_latency_efficiency_ratio = (
            (self.response_average_latency_seconds / self.runtime_response_time_seconds)
            if self.runtime_response_time_seconds > 0
            else 0
        )

        # Total latency Efficiency
        self.throttle_total_latency_efficiency_ratio = (
            (self.response_latency_seconds_total / self.runtime_response_time_seconds)
            if self.runtime_response_time_seconds > 0
            else 0
        )
