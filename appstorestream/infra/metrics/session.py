#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/metrics/session.py                                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday August 15th 2024 04:31:15 pm                                               #
# Modified   : Friday August 16th 2024 10:21:35 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Asynchronous Response Metrics Module"""

import time
from dataclasses import dataclass, field

import aiohttp
import numpy as np
from prometheus_client import Counter, Gauge

from appstorestream.core.metrics import Metrics, MetricServer


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ExtractMetrics(Metrics):
    runtime_start_timestamp_seconds: float = None
    runtime_stop_timestamp_seconds: float = None
    runtime_duration_seconds: float = None

    request_count_total: int = None
    request_per_second_ratio: float = None

    response_count_total: int = None
    response_per_second_ratio: float = None
    response_average_latency_seconds: float = None
    response_latency_seconds_total: float = None
    response_average_size_bytes: int = None
    response_size_bytes_total: int = None

    success_failure_retries_total: int = None
    success_failure_errors_total: int = None
    success_failure_client_errors_total: int = None
    success_failure_server_errors_total: int = None
    success_failure_redirect_errors_total: int = None
    success_failure_unknown_errors_total: int = None
    success_failure_request_failure_rate_ratio: float = None
    success_failure_request_success_rate_ratio: float = None

    throttle_concurrency_efficiency_ratio: float = None
    throttle_average_latency_efficiency_ratio: float = None
    throttle_total_latency_efficiency_ratio: float = None

    latencies: list[float] = field(default_factory=list)

    def start(self) -> None:
        self.runtime_start_timestamp_seconds = time.time()

    def stop(self) -> None:
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
class ExtractMetricServer(MetricServer):
    """Extract Metric Server Class"""

    def __init__(self, job_id: str, dataset: str, port: int = 8000):
        super().__init__(job_id, dataset, port)
        self.define_metrics()

    def define_metrics(self):
        """Defines the metrics for the extract process."""

        # Runtime metrics
        self.extract_runtime_start_timestamp_seconds = Counter(
            "appstorestream_extract_runtime_start_timestamp_seconds",
            "Start timestamp in seconds",
            self._labels.keys(),
        )
        self.extract_runtime_stop_timestamp_seconds = Counter(
            "appstorestream_extract_runtime_stop_timestamp_seconds",
            "Stop timestamp in seconds",
            self._labels.keys(),
        )
        self.extract_runtime_duration_seconds = Gauge(
            "appstorestream_extract_runtime_duration_seconds",
            "Session duration",
            self._labels.keys(),
        )
        self.extract_runtime_duration_seconds_total = Counter(
            "appstorestream_extract_runtime_duration_seconds_total",
            "Session duration",
            self._labels.keys(),
        )

        # Request metrics
        self.extract_request_count_total = Counter(
            "appstorestream_extract_request_count_total",
            "Request count",
            self._labels.keys(),
        )
        self.extract_request_per_second_ratio = Gauge(
            "appstorestream_extract_request_per_second_ratio",
            "Requests per second",
            self._labels.keys(),
        )

        # Response metrics
        self.extract_response_count_total = Counter(
            "appstorestream_extract_response_count_total",
            "Response count",
            self._labels.keys(),
        )
        self.extract_response_per_second_ratio = Gauge(
            "appstorestream_extract_response_per_second_ratio",
            "Responses per second",
            self._labels.keys(),
        )
        self.extract_response_average_latency_seconds = Gauge(
            "appstorestream_extract_response_average_latency_seconds",
            "Average latency for a session",
            self._labels.keys(),
        )
        self.extract_response_latency_seconds_total = Counter(
            "appstorestream_extract_response_latency_seconds_total",
            "Total latency for a session",
            self._labels.keys(),
        )
        self.extract_response_average_size_bytes = Gauge(
            "appstorestream_extract_response_average_size_bytes",
            "Average response size for a session",
            self._labels.keys(),
        )
        self.extract_response_size_bytes_total = Counter(
            "appstorestream_extract_response_size_bytes_total",
            "Total response size for a session",
            self._labels.keys(),
        )

        # Success/Failure metrics
        self.extract_success_failure_retries_total = Counter(
            "appstorestream_extract_success_failure_retries_total",
            "Retry count",
            self._labels.keys(),
        )
        self.extract_success_failure_errors_total = Counter(
            "appstorestream_extract_success_failure_errors_total",
            "Error count",
            self._labels.keys(),
        )
        self.extract_success_failure_client_errors_total = Counter(
            "appstorestream_extract_success_failure_client_errors_total",
            "Client error count",
            self._labels.keys(),
        )
        self.extract_success_failure_server_errors_total = Counter(
            "appstorestream_extract_success_failure_server_errors_total",
            "Server error count",
            self._labels.keys(),
        )
        self.extract_success_failure_redirect_errors_total = Counter(
            "appstorestream_extract_success_failure_redirect_errors_total",
            "Redirect error count",
            self._labels.keys(),
        )
        self.extract_success_failure_unknown_errors_total = Counter(
            "appstorestream_extract_success_failure_unknown_errors_total",
            "Unknown error count",
            self._labels.keys(),
        )
        self.extract_success_failure_request_failure_rate_ratio = Gauge(
            "appstorestream_extract_success_failure_request_failure_rate_ratio",
            "Errors / Requests",
            self._labels.keys(),
        )
        self.extract_success_failure_request_success_rate_ratio = Gauge(
            "appstorestream_extract_success_failure_request_success_rate_ratio",
            "1 - failure_rate",
            self._labels.keys(),
        )

        # Throttle metrics
        self.extract_throttle_concurrency_efficiency_ratio = Gauge(
            "appstorestream_extract_throttle_concurrency_efficiency_ratio",
            "Average latency / (Duration / Requests)",
            self._labels.keys(),
        )
        self.extract_throttle_average_latency_efficiency_ratio = Gauge(
            "appstorestream_extract_throttle_average_latency_efficiency_ratio",
            "Average Latency / Average Duration",
            self._labels.keys(),
        )
        self.extract_throttle_total_latency_efficiency_ratio = Gauge(
            "appstorestream_extract_throttle_total_latency_efficiency_ratio",
            "Total Latency / Total Duration",
            self._labels.keys(),
        )

    def update_metrics(self, metrics: Metrics):
        """Update the metrics with the provided values."""
        metrics = metrics.as_dict()

        # Update the metrics with the provided values
        # Assuming `metrics` is a dictionary containing the new values
        self.extract_runtime_start_timestamp_seconds.labels(**self._labels).inc(
            metrics.get("runtime_start_timestamp_seconds", 0)
        )
        self.extract_runtime_stop_timestamp_seconds.labels(**self._labels).inc(
            metrics.get("runtime_stop_timestamp_seconds", 0)
        )
        self.extract_runtime_duration_seconds.labels(**self._labels).set(
            metrics.get("runtime_duration_seconds", 0)
        )
        self.extract_runtime_duration_seconds_total.labels(**self._labels).inc(
            metrics.get("runtime_duration_seconds", 0)
        )

        self.extract_request_count_total.labels(**self._labels).inc(
            metrics.get("request_count_total", 0)
        )
        self.extract_request_per_second_ratio.labels(**self._labels).set(
            metrics.get("request_per_second_ratio", 0)
        )

        self.extract_response_count_total.labels(**self._labels).inc(
            metrics.get("response_count_total", 0)
        )
        self.extract_response_per_second_ratio.labels(**self._labels).set(
            metrics.get("response_per_second_ratio", 0)
        )
        self.extract_response_average_latency_seconds.labels(**self._labels).set(
            metrics.get("response_average_latency_seconds", 0)
        )
        self.extract_response_latency_seconds_total.labels(**self._labels).inc(
            metrics.get("response_latency_seconds_total", 0)
        )
        self.extract_response_average_size_bytes.labels(**self._labels).set(
            metrics.get("response_average_size_bytes", 0)
        )
        self.extract_response_size_bytes_total.labels(**self._labels).inc(
            metrics.get("response_size_bytes_total", 0)
        )

        self.extract_success_failure_retries_total.labels(**self._labels).inc(
            metrics.get("success_failure_retries_total", 0)
        )
        self.extract_success_failure_errors_total.labels(**self._labels).inc(
            metrics.get("success_failure_errors_total", 0)
        )
        self.extract_success_failure_client_errors_total.labels(**self._labels).inc(
            metrics.get("success_failure_client_errors_total", 0)
        )
        self.extract_success_failure_server_errors_total.labels(**self._labels).inc(
            metrics.get("success_failure_server_errors_total", 0)
        )
        self.extract_success_failure_redirect_errors_total.labels(**self._labels).inc(
            metrics.get("success_failure_redirect_errors_total", 0)
        )
        self.extract_success_failure_unknown_errors_total.labels(**self._labels).inc(
            metrics.get("success_failure_unknown_errors_total", 0)
        )
        self.extract_success_failure_request_failure_rate_ratio.labels(
            **self._labels
        ).set(metrics.get("success_failure_request_failure_rate_ratio", 0))
        self.extract_success_failure_request_success_rate_ratio.labels(
            **self._labels
        ).set(metrics.get("success_failure_request_success_rate_ratio", 0))

        self.extract_throttle_concurrency_efficiency_ratio.labels(**self._labels).set(
            metrics.get("throttle_concurrency_efficiency_ratio", 0)
        )
        self.extract_throttle_average_latency_efficiency_ratio.labels(
            **self._labels
        ).set(metrics.get("throttle_average_latency_efficiency_ratio", 0))
        self.extract_throttle_total_latency_efficiency_ratio.labels(**self._labels).set(
            metrics.get("throttle_total_latency_efficiency_ratio", 0)
        )
