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
# Modified   : Tuesday September 3rd 2024 10:28:33 pm                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Extract Observer Module"""
import logging
from typing import TypeVar

from prometheus_client import Counter, Histogram

from appvocai.core.enum import ContentType
from appvocai.infra.observer.base import Observer
from appvocai.infra.web.extractor import MetricsExtractor

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
T = TypeVar("T")


# ------------------------------------------------------------------------------------------------ #
class ObserverExtractorMetrics(Observer):
    """
    Observer class for updating extractor-related Prometheus metrics.
    """

    def __init__(self, content_type: ContentType):
        super().__init__(content_type)

    def _setup_metrics(self) -> None:
        """
        Sets up the Prometheus metrics specific to the extractor task.
        """
        # Counter metrics
        self.extractor_requests_total = Counter(
            "appvocai_extractor_requests_total",
            "Total Number Of Requests",
            ["content_type"],
        )

        self.extractor_response_size_bytes_total = Counter(
            "appvocai_extractor_response_size_bytes_total",
            "Total Bytes From Responses In Session",
            ["content_type"],
        )

        self.extractor_errors_total = Counter(
            "appvocai_extractor_errors_total",
            "Total Errors Session",
            ["content_type", "error_code", "error_description"],
        )

        # Histogram Metrics
        self.extractor_session_control_rate_ratio = Histogram(
            "appvocai_extractor_session_control_rate_ratio",
            "Inverse of Duration * Concurrency",
            ["content_type"],
        )
        self.extractor_session_control_concurrency = Histogram(
            "appvocai_extractor_session_control_concurrency",
            "Concurrency computed by the Adapter ",
            ["content_type"],
        )

        self.extractor_duration_seconds = Histogram(
            "appvocai_extractor_duration_seconds",
            "Duration Of Session",
            ["content_type"],
        )
        self.extractor_latency_average_seconds = Histogram(
            "appvocai_extractor_latency_average_seconds",
            "Average Latency Within Session",
            ["content_type"],
        )
        self.extractor_speedup_ratio = Histogram(
            "appvocai_extractor_speedup_ratio",
            "Ratio Of Total Latency And Duration",
            ["content_type"],
        )
        self.extractor_throughput_ratio = Histogram(
            "appvocai_extractor_throughput_ratio",
            "Ratio Of Requests And Duration",
            ["content_type"],
        )

    def notify(self, metrics: MetricsExtractor) -> None:
        """
        Updates the Prometheus metrics with data from a MetricsExtract object.

        Args:
            metrics (MetricsExtract): The extractor metrics object containing the data to be updated.
        """
        # Validate the metrics.
        metrics.validate()
        try:
            # Update Counters
            self.extractor_requests_total.labels(
                content_type=metrics.content_type.value
            ).inc(metrics.requests)

            self.extractor_response_size_bytes_total.labels(
                content_type=metrics.content_type.value
            ).inc(metrics.response_size)

            # Count errors
            for error_status_code in metrics.error_status_codes:
                self.extractor_errors_total.labels(
                    content_type=metrics.content_type.value,
                    error_code=error_status_code,
                ).inc()

            # Histogram metrics.
            self.extractor_session_control_rate_ratio.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.session_control_rate)
            self.extractor_session_control_concurrency.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.session_control_concurrency)
            self.extractor_duration_seconds.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.duration)
            self.extractor_latency_average_seconds.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.latency_average)
            self.extractor_speedup_ratio.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.speedup)
            self.extractor_throughput_ratio.labels(
                content_type=metrics.content_type.value
            ).observe(metrics.throughput)

        except Exception as e:
            logger.error(f"Failed to update metrics: {e}", exc_info=True)
