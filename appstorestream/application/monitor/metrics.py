#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/monitor/metrics.py                                      #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday August 15th 2024 11:26:23 pm                                               #
# Modified   : Friday August 16th 2024 03:05:48 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import time
from dataclasses import dataclass
from prometheus_client import Counter, Gauge

from appstorestream.core.metrics import Metrics, MetricServer
from appstorestream.core.data import DataClass

# ------------------------------------------------------------------------------------------------ #


class TaskMetricServer(MetricServer):
    def __init__(self, job_id: str, dataset: str, port: int = 8000):
        super().__init__(job_id=job_id, dataset=dataset, port=port)

        self.define_metrics()

        self._start_timestamp = None
        self._stop_timestamp = None
        self._runtime = None

    def define_metrics(self) -> None:
        # Define metrics with labels
        # Runtime metrics
        self.job_runtime_seconds = Gauge(
            "job_runtime_seconds", "Job runtime in seconds", ["job_id", "dataset"]
        )
        self.job_start_timestamp_seconds = Gauge(
            "job_start_timestamp_seconds",
            "Job start timestamp in seconds",
            ["job_id", "dataset"],
        )
        self.job_stop_timestamp_seconds = Gauge(
            "job_stop_timestamp_seconds",
            "Job stop timestamp in seconds",
            ["job_id", "dataset"],
        )

        # Workload metrics
        self.job_records_total = Counter(
            "job_records_total", "Records processed by job", ["job_id", "dataset"]
        )
        self.job_requests_total = Counter(
            "job_requests_total", "Requests processed by job", ["job_id", "dataset"]
        )
        self.job_responses_total = Counter(
            "job_responses_total", "Responses received by job", ["job_id", "dataset"]
        )
        self.job_sessions_total = Counter(
            "job_sessions_total", "Sessions processed by job", ["job_id", "dataset"]
        )

        # Payload metrics
        self.job_response_size_bytes = Counter(
            "job_response_size_bytes",
            "Sum of response sizes for job",
            ["job_id", "dataset"],
        )
        self.job_average_response_size_bytes = Gauge(
            "job_average_response_size_bytes",
            "Response size / Responses",
            ["job_id", "dataset"],
        )

        # Throughput metrics
        self.job_records_per_second_ratio = Gauge(
            "job_records_per_second_ratio",
            "Records processed per second for job",
            ["job_id", "dataset"],
        )
        self.job_requests_per_second_ratio = Gauge(
            "job_requests_per_second_ratio",
            "Requests processed per second for job",
            ["job_id", "dataset"],
        )
        self.job_responses_per_second_ratio = Gauge(
            "job_responses_per_second_ratio",
            "Responses processed per second for job",
            ["job_id", "dataset"],
        )

        # Success/Failure metrics
        self.job_errors_total = Counter(
            "job_errors_total", "Errors encountered during job", ["job_id", "dataset"]
        )
        self.job_client_errors_total = Counter(
            "job_client_errors_total",
            "Client errors encountered during job",
            ["job_id", "dataset"],
        )
        self.job_server_errors_total = Counter(
            "job_server_errors_total",
            "Server errors encountered during job",
            ["job_id", "dataset"],
        )
        self.job_redirect_errors_total = Counter(
            "job_redirect_errors_total",
            "Redirect errors encountered during job",
            ["job_id", "dataset"],
        )
        self.job_unknown_errors_total = Counter(
            "job_unknown_errors_total",
            "Unknown errors encountered during job",
            ["job_id", "dataset"],
        )
        self.job_data_errors_total = Counter(
            "job_data_errors_total",
            "Data errors encountered during job",
            ["job_id", "dataset"],
        )
        self.job_retries_total = Gauge(
            "job_retries_total", "Number of retries", ["job_id", "dataset"]
        )
        self.job_request_failure_rate_ratio = Gauge(
            "job_request_failure_rate_ratio", "Errors / Requests", ["job_id", "dataset"]
        )
        self.job_request_success_rate_ratio = Gauge(
            "job_request_success_rate_ratio", "1 - failure_rate", ["job_id", "dataset"]
        )

        # Web metrics
        self.job_request_latency_seconds_total = Counter(
            "job_request_latency_seconds_total",
            "Total latency for job",
            ["job_id", "dataset"],
        )
        self.job_session_duration_seconds_total = Counter(
            "job_session_duration_seconds_total",
            "Total session durations for job",
            ["job_id", "dataset"],
        )
        self.job_concurrency_efficiency_ratio = Gauge(
            "job_concurrency_efficiency_ratio",
            "Average latency / (Duration / Requests)",
            ["job_id", "dataset"],
        )
        self.job_average_latency_efficiency_ratio = Gauge(
            "job_average_latency_efficiency_ratio",
            "Average Latency / Average Duration",
            ["job_id", "dataset"],
        )
        self.job_total_latency_efficiency_ratio = Gauge(
            "job_total_latency_efficiency_ratio",
            "Total Latency / Total Duration",
            ["job_id", "dataset"],
        )
        self.job_average_request_latency_seconds = Gauge(
            "job_average_request_latency_seconds",
            "Total Request Latency / Requests",
            ["job_id", "dataset"],
        )
        self.job_average_session_duration_seconds = Gauge(
            "job_average_session_duration_seconds",
            "Total Session Duration / Sessions",
            ["job_id", "dataset"],
        )
        self.job_latency_standard_deviation_seconds = Gauge(
            "job_latency_standard_deviation_seconds",
            "Standard deviation of latencies over job",
            ["job_id", "dataset"],
        )
        self.job_latency_coefficient_of_variation_seconds = Gauge(
            "job_latency_coefficient_of_variation_seconds",
            "Standard Deviation over Average Latency",
            ["job_id", "dataset"],
        )

        # System metrics
        self.job_network_io_bytes = Counter(
            "job_network_io_bytes", "Network IO for job", ["job_id", "dataset"]
        )
        self.job_disk_io_bytes = Counter(
            "job_disk_io_bytes", "Disk IO for job", ["job_id", "dataset"]
        )
        self.job_average_cpu_percent_ratio = Gauge(
            "job_average_cpu_percent_ratio",
            "Average CPU Percent for Job",
            ["job_id", "dataset"],
        )

    def start(self) -> None:
        self._start_timestamp = time.time()

    def stop(self) -> None:
        self._stop_timestamp = time.time()
        self._runtime = self._stop_timestamp - self._start_timestamp

    def update_metrics(self, metrics:  int) -> None: