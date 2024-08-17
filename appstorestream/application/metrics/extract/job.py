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
# Modified   : Saturday August 17th 2024 12:43:35 pm                                               #
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


# ------------------------------------------------------------------------------------------------ #
class ExtractJobMetricsExporter(MetricsExporter):
    """Extract Metric Server Class"""

    _category = "extract"
    _level = "job"

    def __init__(
        self,
        job_id: str,
        dataset: str,
        port: int = 8000,
        registry: CollectorRegistry = None,
    ):
        super().__init__(job_id=job_id, dataset=dataset, port=port, registry=registry)

        self.define_metrics()

    def define_metrics(self):
        """Defines the metrics for the extract process."""

        metrics_config = self.load_config(category=self._category, level=self._level)

        # Runtime metrics
        self.extract_runtime_start_timestamp_seconds = self.get_or_create_metric(
            metric_name="appstorestream_extract_runtime_start_timestamp_seconds",
            metric_type=metrics_config[
                "appstorestream_extract_runtime_start_timestamp_seconds"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_runtime_start_timestamp_seconds"
            ]["Description"],
            labels=self.labels.keys(),
        )

        self.extract_runtime_stop_timestamp_seconds = self.get_or_create_metric(
            metric_name="appstorestream_extract_runtime_stop_timestamp_seconds",
            metric_type=metrics_config[
                "appstorestream_extract_runtime_stop_timestamp_seconds"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_runtime_stop_timestamp_seconds"
            ]["Description"],
            labels=self.labels.keys(),
        )
        self.extract_runtime_duration_seconds = self.get_or_create_metric(
            metric_name="appstorestream_extract_runtime_duration_seconds",
            metric_type=metrics_config[
                "appstorestream_extract_runtime_duration_seconds"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_runtime_duration_seconds"
            ]["Description"],
            labels=self.labels.keys(),
        )
        self.extract_runtime_duration_seconds_total = self.get_or_create_metric(
            metric_name="appstorestream_extract_runtime_duration_seconds_total",
            metric_type=metrics_config[
                "appstorestream_extract_runtime_duration_seconds_total"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_runtime_duration_seconds_total"
            ]["Description"],
            labels=self.labels.keys(),
        )

        # Request metrics
        self.extract_request_count_total = self.get_or_create_metric(
            metric_name="appstorestream_extract_request_count_total",
            metric_type=metrics_config["appstorestream_extract_request_count_total"][
                "Type"
            ],
            description=metrics_config["appstorestream_extract_request_count_total"][
                "Description"
            ],
            labels=self.labels.keys(),
        )
        self.extract_request_per_second_ratio = self.get_or_create_metric(
            metric_name="appstorestream_extract_request_per_second_ratio",
            metric_type=metrics_config[
                "appstorestream_extract_request_per_second_ratio"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_request_per_second_ratio"
            ]["Description"],
            labels=self.labels.keys(),
        )

        # Response metrics

        self.extract_response_count_total = self.get_or_create_metric(
            metric_name="appstorestream_extract_response_count_total",
            metric_type=metrics_config["appstorestream_extract_response_count_total"][
                "Type"
            ],
            description=metrics_config["appstorestream_extract_response_count_total"][
                "Description"
            ],
            labels=self.labels.keys(),
        )
        self.extract_response_per_second_ratio = self.get_or_create_metric(
            metric_name="appstorestream_extract_response_per_second_ratio",
            metric_type=metrics_config[
                "appstorestream_extract_response_per_second_ratio"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_response_per_second_ratio"
            ]["Description"],
            labels=self.labels.keys(),
        )
        self.extract_response_average_latency_seconds = self.get_or_create_metric(
            metric_name="appstorestream_extract_response_average_latency_seconds",
            metric_type=metrics_config[
                "appstorestream_extract_response_average_latency_seconds"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_response_average_latency_seconds"
            ]["Description"],
            labels=self.labels.keys(),
        )
        self.extract_response_latency_seconds_total = self.get_or_create_metric(
            metric_name="appstorestream_extract_response_latency_seconds_total",
            metric_type=metrics_config[
                "appstorestream_extract_response_latency_seconds_total"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_response_latency_seconds_total"
            ]["Description"],
            labels=self.labels.keys(),
        )
        self.extract_response_average_size_bytes = self.get_or_create_metric(
            metric_name="appstorestream_extract_response_average_size_bytes",
            metric_type=metrics_config[
                "appstorestream_extract_response_average_size_bytes"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_response_average_size_bytes"
            ]["Description"],
            labels=self.labels.keys(),
        )
        self.extract_response_size_bytes_total = self.get_or_create_metric(
            metric_name="appstorestream_extract_response_size_bytes_total",
            metric_type=metrics_config[
                "appstorestream_extract_response_size_bytes_total"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_response_size_bytes_total"
            ]["Description"],
            labels=self.labels.keys(),
        )

        # Success/Failure metrics
        self.extract_success_failure_retries_total = self.get_or_create_metric(
            metric_name="appstorestream_extract_success_failure_retries_total",
            metric_type=metrics_config[
                "appstorestream_extract_success_failure_retries_total"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_success_failure_retries_total"
            ]["Description"],
            labels=self.labels.keys(),
        )
        self.extract_success_failure_errors_total = self.get_or_create_metric(
            metric_name="appstorestream_extract_success_failure_errors_total",
            metric_type=metrics_config[
                "appstorestream_extract_success_failure_errors_total"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_success_failure_errors_total"
            ]["Description"],
            labels=self.labels.keys(),
        )
        self.extract_success_failure_client_errors_total = self.get_or_create_metric(
            metric_name="appstorestream_extract_success_failure_client_errors_total",
            metric_type=metrics_config[
                "appstorestream_extract_success_failure_client_errors_total"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_success_failure_client_errors_total"
            ]["Description"],
            labels=self.labels.keys(),
        )
        self.extract_success_failure_server_errors_total = self.get_or_create_metric(
            metric_name="appstorestream_extract_success_failure_server_errors_total",
            metric_type=metrics_config[
                "appstorestream_extract_success_failure_server_errors_total"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_success_failure_server_errors_total"
            ]["Description"],
            labels=self.labels.keys(),
        )
        self.extract_success_failure_redirect_errors_total = self.get_or_create_metric(
            metric_name="appstorestream_extract_success_failure_redirect_errors_total",
            metric_type=metrics_config[
                "appstorestream_extract_success_failure_redirect_errors_total"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_success_failure_redirect_errors_total"
            ]["Description"],
            labels=self.labels.keys(),
        )
        self.extract_success_failure_unknown_errors_total = self.get_or_create_metric(
            metric_name="appstorestream_extract_success_failure_unknown_errors_total",
            metric_type=metrics_config[
                "appstorestream_extract_success_failure_unknown_errors_total"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_success_failure_unknown_errors_total"
            ]["Description"],
            labels=self.labels.keys(),
        )
        self.extract_success_failure_request_failure_rate_ratio = self.get_or_create_metric(
            metric_name="appstorestream_extract_success_failure_request_failure_rate_ratio",
            metric_type=metrics_config[
                "appstorestream_extract_success_failure_request_failure_rate_ratio"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_success_failure_request_failure_rate_ratio"
            ]["Description"],
            labels=self.labels.keys(),
        )
        self.extract_success_failure_request_success_rate_ratio = self.get_or_create_metric(
            metric_name="appstorestream_extract_success_failure_request_success_rate_ratio",
            metric_type=metrics_config[
                "appstorestream_extract_success_failure_request_success_rate_ratio"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_success_failure_request_success_rate_ratio"
            ]["Description"],
            labels=self.labels.keys(),
        )

        # Throttle metrics
        self.extract_throttle_concurrency_efficiency_ratio = self.get_or_create_metric(
            metric_name="appstorestream_extract_throttle_concurrency_efficiency_ratio",
            metric_type=metrics_config[
                "appstorestream_extract_throttle_concurrency_efficiency_ratio"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_throttle_concurrency_efficiency_ratio"
            ]["Description"],
            labels=self.labels.keys(),
        )
        self.extract_throttle_average_latency_efficiency_ratio = self.get_or_create_metric(
            metric_name="appstorestream_extract_throttle_average_latency_efficiency_ratio",
            metric_type=metrics_config[
                "appstorestream_extract_throttle_average_latency_efficiency_ratio"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_throttle_average_latency_efficiency_ratio"
            ]["Description"],
            labels=self.labels.keys(),
        )

        self.extract_throttle_total_latency_efficiency_ratio = self.get_or_create_metric(
            metric_name="appstorestream_extract_throttle_total_latency_efficiency_ratio",
            metric_type=metrics_config[
                "appstorestream_extract_throttle_total_latency_efficiency_ratio"
            ]["Type"],
            description=metrics_config[
                "appstorestream_extract_throttle_total_latency_efficiency_ratio"
            ]["Description"],
            labels=self.labels.keys(),
        )

    def update_metrics(self, metrics: Metrics):
        """Update the metrics with the provided values."""
        metrics = metrics.as_dict()

        # Update the metrics with the provided values
        # Assuming `metrics` is a dictionary containing the new values
        self.extract_runtime_start_timestamp_seconds.labels(**self.labels).inc(
            metrics.get("runtime_start_timestamp_seconds", 0)
        )
        self.extract_runtime_stop_timestamp_seconds.labels(**self.labels).inc(
            metrics.get("runtime_stop_timestamp_seconds", 0)
        )
        self.extract_runtime_duration_seconds.labels(**self.labels).set(
            metrics.get("runtime_duration_seconds", 0)
        )
        self.extract_runtime_duration_seconds_total.labels(**self.labels).inc(
            metrics.get("runtime_duration_seconds", 0)
        )

        self.extract_request_count_total.labels(**self.labels).inc(
            metrics.get("request_count_total", 0)
        )
        self.extract_request_per_second_ratio.labels(**self.labels).set(
            metrics.get("request_per_second_ratio", 0)
        )

        self.extract_response_count_total.labels(**self.labels).inc(
            metrics.get("response_count_total", 0)
        )
        self.extract_response_per_second_ratio.labels(**self.labels).set(
            metrics.get("response_per_second_ratio", 0)
        )
        self.extract_response_average_latency_seconds.labels(**self.labels).set(
            metrics.get("response_average_latency_seconds", 0)
        )
        self.extract_response_latency_seconds_total.labels(**self.labels).inc(
            metrics.get("response_latency_seconds_total", 0)
        )
        self.extract_response_average_size_bytes.labels(**self.labels).set(
            metrics.get("response_average_size_bytes", 0)
        )
        self.extract_response_size_bytes_total.labels(**self.labels).inc(
            metrics.get("response_size_bytes_total", 0)
        )

        self.extract_success_failure_retries_total.labels(**self.labels).inc(
            metrics.get("success_failure_retries_total", 0)
        )
        self.extract_success_failure_errors_total.labels(**self.labels).inc(
            metrics.get("success_failure_errors_total", 0)
        )
        self.extract_success_failure_client_errors_total.labels(**self.labels).inc(
            metrics.get("success_failure_client_errors_total", 0)
        )
        self.extract_success_failure_server_errors_total.labels(**self.labels).inc(
            metrics.get("success_failure_server_errors_total", 0)
        )
        self.extract_success_failure_redirect_errors_total.labels(**self.labels).inc(
            metrics.get("success_failure_redirect_errors_total", 0)
        )
        self.extract_success_failure_unknown_errors_total.labels(**self.labels).inc(
            metrics.get("success_failure_unknown_errors_total", 0)
        )
        self.extract_success_failure_request_failure_rate_ratio.labels(
            **self.labels
        ).set(metrics.get("success_failure_request_failure_rate_ratio", 0))
        self.extract_success_failure_request_success_rate_ratio.labels(
            **self.labels
        ).set(metrics.get("success_failure_request_success_rate_ratio", 0))

        self.extract_throttle_concurrency_efficiency_ratio.labels(**self.labels).set(
            metrics.get("throttle_concurrency_efficiency_ratio", 0)
        )
        self.extract_throttle_average_latency_efficiency_ratio.labels(
            **self.labels
        ).set(metrics.get("throttle_average_latency_efficiency_ratio", 0))
        self.extract_throttle_total_latency_efficiency_ratio.labels(**self.labels).set(
            metrics.get("throttle_total_latency_efficiency_ratio", 0)
        )
