#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/observer/extract.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 08:53:14 pm                                               #
# Modified   : Friday September 6th 2024 05:45:34 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Extract Observer Module"""
import logging
from typing import TypeVar

from prometheus_client import Counter, Histogram

from appvocai.application.metrics.extract import MetricsAsyncSession
from appvocai.core.enum import DataType
from appvocai.infra.observer.base import Observer

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
T = TypeVar("T")


# ------------------------------------------------------------------------------------------------ #
class ObserverAsyncSessionMetrics(Observer[MetricsAsyncSession]):
    """
    Observer class for updating async_session-related Prometheus metrics.
    """

    def __init__(self, content_type: DataType):
        super().__init__(content_type)

    def _setup_metrics(self) -> None:
        """
        Sets up the Prometheus metrics specific to the async_session task.
        """
        # Counter metrics
        self.async_session_requests_total = Counter(
            "appvocai_async_session_requests_total",
            "Total Number Of Requests",
            ["content_type"],
        )

        self.async_session_response_size_bytes_total = Counter(
            "appvocai_async_session_response_size_bytes_total",
            "Total Bytes From Responses In Session",
            ["content_type"],
        )

        self.async_session_errors_total = Counter(
            "appvocai_async_session_errors_total",
            "Total Errors Session",
            ["content_type", "error_code", "error_description"],
        )

        # Histogram Metrics
        self.async_session_session_control_rate_ratio = Histogram(
            "appvocai_async_session_session_control_rate_ratio",
            "Inverse of Duration * Concurrency",
            ["content_type"],
        )
        self.async_session_session_control_concurrency = Histogram(
            "appvocai_async_session_session_control_concurrency",
            "Concurrency computed by the Adapter ",
            ["content_type"],
        )

        self.async_session_duration_seconds = Histogram(
            "appvocai_async_session_duration_seconds",
            "Duration Of Session",
            ["content_type"],
        )
        self.async_session_latency_average_seconds = Histogram(
            "appvocai_async_session_latency_average_seconds",
            "Average Latency Within Session",
            ["content_type"],
        )
        self.async_session_speedup_ratio = Histogram(
            "appvocai_async_session_speedup_ratio",
            "Ratio Of Total Latency And Duration",
            ["content_type"],
        )
        self.async_session_throughput_ratio = Histogram(
            "appvocai_async_session_throughput_ratio",
            "Ratio Of Requests And Duration",
            ["content_type"],
        )

    def notify(self, metrics: MetricsAsyncSession) -> None:
        """
        Updates the Prometheus metrics with data from a MetricsExtract object.

        Args:
            metrics (MetricsExtract): The async_session metrics object containing the data to be updated.
        """
        # Validate the metrics.
        metrics.validate()
        try:
            # Update Counters
            self.async_session_requests_total.labels(
                content_type=metrics.content_type.value
            ).inc(metrics.requests)

            self.async_session_response_size_bytes_total.labels(
                content_type=metrics.content_type.value
            ).inc(metrics.response_size)

            # Count errors
            for error_status_code in metrics.error_status_codes:
                self.async_session_errors_total.labels(
                    content_type=metrics.content_type.value,
                    error_code=error_status_code,
                ).inc()

            # Histogram metrics.
            self.async_session_session_control_rate_ratio.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.session_control_rate)
            self.async_session_session_control_concurrency.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.session_control_concurrency)
            self.async_session_duration_seconds.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.duration)
            self.async_session_latency_average_seconds.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.latency_average)
            self.async_session_speedup_ratio.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.speedup)
            self.async_session_throughput_ratio.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.throughput)

        except Exception as e:
            logger.error(f"Failed to update metrics: {e}", exc_info=True)
