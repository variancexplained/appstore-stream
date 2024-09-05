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
# Modified   : Thursday September 5th 2024 06:58:09 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Extract Observer Module"""
import logging
from typing import TypeVar

from prometheus_client import Counter, Histogram

from appvocai.application.metrics.extract import MetricsASession
from appvocai.core.enum import DataType
from appvocai.infra.observer.base import Observer

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
T = TypeVar("T")


# ------------------------------------------------------------------------------------------------ #
class ObserverASessionMetrics(Observer[MetricsASession]):
    """
    Observer class for updating asession-related Prometheus metrics.
    """

    def __init__(self, content_type: DataType):
        super().__init__(content_type)

    def _setup_metrics(self) -> None:
        """
        Sets up the Prometheus metrics specific to the asession task.
        """
        # Counter metrics
        self.asession_requests_total = Counter(
            "appvocai_asession_requests_total",
            "Total Number Of Requests",
            ["content_type"],
        )

        self.asession_response_size_bytes_total = Counter(
            "appvocai_asession_response_size_bytes_total",
            "Total Bytes From Responses In Session",
            ["content_type"],
        )

        self.asession_errors_total = Counter(
            "appvocai_asession_errors_total",
            "Total Errors Session",
            ["content_type", "error_code", "error_description"],
        )

        # Histogram Metrics
        self.asession_session_control_rate_ratio = Histogram(
            "appvocai_asession_session_control_rate_ratio",
            "Inverse of Duration * Concurrency",
            ["content_type"],
        )
        self.asession_session_control_concurrency = Histogram(
            "appvocai_asession_session_control_concurrency",
            "Concurrency computed by the Adapter ",
            ["content_type"],
        )

        self.asession_duration_seconds = Histogram(
            "appvocai_asession_duration_seconds",
            "Duration Of Session",
            ["content_type"],
        )
        self.asession_latency_average_seconds = Histogram(
            "appvocai_asession_latency_average_seconds",
            "Average Latency Within Session",
            ["content_type"],
        )
        self.asession_speedup_ratio = Histogram(
            "appvocai_asession_speedup_ratio",
            "Ratio Of Total Latency And Duration",
            ["content_type"],
        )
        self.asession_throughput_ratio = Histogram(
            "appvocai_asession_throughput_ratio",
            "Ratio Of Requests And Duration",
            ["content_type"],
        )

    def notify(self, metrics: MetricsASession) -> None:
        """
        Updates the Prometheus metrics with data from a MetricsExtract object.

        Args:
            metrics (MetricsExtract): The asession metrics object containing the data to be updated.
        """
        # Validate the metrics.
        metrics.validate()
        try:
            # Update Counters
            self.asession_requests_total.labels(
                content_type=metrics.content_type.value
            ).inc(metrics.requests)

            self.asession_response_size_bytes_total.labels(
                content_type=metrics.content_type.value
            ).inc(metrics.response_size)

            # Count errors
            for error_status_code in metrics.error_status_codes:
                self.asession_errors_total.labels(
                    content_type=metrics.content_type.value,
                    error_code=error_status_code,
                ).inc()

            # Histogram metrics.
            self.asession_session_control_rate_ratio.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.session_control_rate)
            self.asession_session_control_concurrency.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.session_control_concurrency)
            self.asession_duration_seconds.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.duration)
            self.asession_latency_average_seconds.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.latency_average)
            self.asession_speedup_ratio.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.speedup)
            self.asession_throughput_ratio.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.throughput)

        except Exception as e:
            logger.error(f"Failed to update metrics: {e}", exc_info=True)
