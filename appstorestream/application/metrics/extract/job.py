#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/metrics/extract/job.py                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 17th 2024 11:14:17 am                                               #
# Modified   : Saturday August 17th 2024 12:04:31 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Extract Job Metric Module"""
import time
from dataclasses import dataclass, field

import aiohttp
import numpy as np
from prometheus_client import CollectorRegistry

from appstorestream.core.metrics import Metrics, MetricsExporter


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ExtractJobMetrics(Metrics):
    extract_job_runtime_start_timestamp_seconds: float = 0.0
    extract_job_runtime_stop_timestamp_seconds: float = 0.0
    extract_job_runtime_duration_seconds_total: float = 0.0

    extract_job_request_session_count_total: float = 0.0
    extract_job_request_count_total: int = 0
    extract_job_request_per_second_ratio: float = 0.0

    extract_job_response_count_total: int = 0
    extract_job_response_per_second_ratio: float = 0.0
    extract_job_response_average_latency_seconds: float = 0.0
    extract_job_response_latency_seconds_total: float = 0.0
    extract_job_response_average_size_bytes: int = 0
    extract_job_response_size_bytes_total: int = 0

    extract_job_success_failure_retries_total: int = 0
    extract_job_success_failure_errors_total: int = 0
    extract_job_success_failure_request_failure_rate_ratio: float = 0.0
    extract_job_success_failure_request_success_rate_ratio: float = 0.0

    def update_metrics(self, task_metrics: Metrics) -> None:
        self._update_runtime_metrics(task_metrics=task_metrics)
        self._update_request_metrics(task_metrics=task_metrics)
        self._update_response_metrics(task_metrics=task_metrics)
        self._update_success_failure_metrics(task_metrics=task_metrics)

    def _update_runtime_metrics(self, task_metrics: Metrics) -> None:
        # Sets runtime start timestamp if not already set.
        self.extract_job_runtime_stop_timestamp_seconds = (
            self.extract_job_runtime_stop_timestamp_seconds
            or task_metrics.extract_task_runtime_start_timestamp_seconds
        )
        # Sets runtime stop to task stop in case of job failure, we
        # have the most recent timestamp
        self.extract_job_runtime_stop_timestamp_seconds = (
            task_metrics.extract_task_runtime_stop_timestamp_seconds
        )
        # Increment job duration
        self.extract_job_runtime_duration_seconds_total += (
            task_metrics.extract_task_runtime_duration_seconds
        )

    def _update_request_metrics(self, task_metrics: Metrics) -> None:
        # Session count
        self.extract_job_request_session_count_total += 1
        # Request Count
        self.extract_job_request_count_total += (
            task_metrics.extract_task_request_count_total
        )
        # Requests per Second
        self.extract_job_request_per_second_ratio = (
            self.extract_job_request_count_total
            / self.extract_job_runtime_duration_seconds_total
        )

    def _update_response_metrics(self, task_metrics: Metrics) -> None:
        # Response Count
        self.extract_job_response_count_total += (
            task_metrics.extract_task_response_count_total
        )
        # Responses per Second
        self.extract_job_response_per_second_ratio = (
            self.extract_job_response_count_total
            / self.extract_job_runtime_duration_seconds_total
        )

        # Total Latency
        self.extract_job_response_latency_seconds_total += (
            task_metrics.extract_task_response_latency_seconds_total
        )
        # Average Latency
        self.extract_job_response_average_latency_seconds = (
            self.extract_job_response_latency_seconds_total
            / self.extract_job_response_count_total
        )

        # Total Size of Responses
        self.extract_job_response_size_bytes_total += (
            task_metrics.extract_task_response_size_bytes_total
        )
        # Average response size
        self.extract_job_response_average_size_bytes = (
            self.extract_job_response_size_bytes_total
            / self.extract_job_response_count_total
        )

    def _update_success_failure_metrics(self, task_metrics: Metrics) -> None:
        # Retries
        self.extract_job_success_failure_retries_total += (
            task_metrics.extract_task_success_failure_retries_total
        )
        # Errors
        self.extract_job_success_failure_errors_total += (
            task_metrics.extract_task_success_failure_errors_total
        )
        # Failure Rate
        self.extract_job_success_failure_request_failure_rate_ratio = (
            self.extract_job_success_failure_errors_total
            / self.extract_job_request_count_total
        )
        # Success Rate
        self.extract_job_success_failure_request_success_rate_ratio = (
            1 - self.extract_job_success_failure_request_failure_rate_ratio
        )
