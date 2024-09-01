#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/observer/extract.py                                           #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 08:53:14 pm                                               #
# Modified   : Sunday September 1st 2024 12:49:01 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Extract Observer Module"""
import logging
from typing import TypeVar

from prometheus_client import Counter, Gauge, Histogram

from appvocai.application.observer.base import Observer
from appvocai.core.enum import ContentType
from appvocai.domain.metrics.extract import MetricsExtract

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
T = TypeVar('T')
# ------------------------------------------------------------------------------------------------ #
class ObserverExtractMetrics(Observer[MetricsExtract]):
    """
    Observer class for updating extract-related Prometheus metrics.
    """
    def __init__(self, content_type: ContentType):
        super().__init__(content_type)

    def _setup_metrics(self) -> None:
        """
        Sets up the Prometheus metrics specific to the extract task.
        """
        # Counter metrics
        self.extract_records_total = Counter(
            'appvocai_extract_records_total',
            'Total Number Of Records',
            ['content_type']
        )
        self.extract_requests_total = Counter(
            'appvocai_extract_requests_total',
            'Total Number Of Requests',
            ['content_type']
        )

        # Gauge Metrics
        self.extract_errors = Gauge(
            'appvocai_extract_errors',
            'Number Of Errors In Extract Step',
            ['content_type']
        )
        self.extract_records = Gauge(
            'appvocai_extract_records',
            'Number Of Records Within A Session',
            ['content_type']
        )
        self.extract_requests = Gauge(
            'appvocai_extract_requests',
            'Number Of Requests Within A Session',
            ['content_type']
        )
        self.extract_response_size_bytes = Gauge(
            'appvocai_extract_response_size_bytes',
            'Total Bytes From Responses In Session',
            ['content_type']
        )

        # Histogram Metrics
        self.extract_session_control_rate_ratio = Histogram(
            'appvocai_extract_session_control_rate_ratio',
            'Inverse of Duration * Concurrency',
            ['content_type']
        )
        self.extract_session_control_concurrency = Histogram(
            'appvocai_extract_session_control_concurrency',
            'Concurrency computed by the Adapter ',
            ['content_type']
        )

        self.extract_duration_seconds = Histogram(
            'appvocai_extract_duration_seconds',
            'Duration Of Session',
            ['content_type']
        )
        self.extract_latency_average_seconds = Histogram(
            'appvocai_extract_latency_average_seconds',
            'Average Latency Within Session',
            ['content_type']
        )
        self.extract_speedup_ratio = Histogram(
            'appvocai_extract_speedup_ratio',
            'Ratio Of Total Latency And Duration',
            ['content_type']
        )
        self.extract_throughput_ratio = Histogram(
            'appvocai_extract_throughput_ratio',
            'Ratio Of Requests And Duration',
            ['content_type']
        )

    def notify(self, metrics: MetricsExtract) -> None:
        """
        Updates the Prometheus metrics with data from a MetricsExtract object.

        Args:
            metrics (MetricsExtract): The extract metrics object containing the data to be updated.
        """
        # Validate the metrics.
        metrics.validate()
        try:
            # Update Counters
            self.extract_records_total.labels(content_type=self._content_type.value).inc(metrics.records)
            self.extract_requests_total.labels(content_type=self._content_type.value).inc(metrics.requests)

            # Gauge Metrics
            self.extract_errors.labels(content_type=self._content_type.value).set(metrics.errors)
            self.extract_records.labels(content_type=self._content_type.value).set(metrics.records)
            self.extract_requests.labels(content_type=self._content_type.value).set(metrics.requests)
            self.extract_response_size_bytes.labels(content_type=self._content_type.value).set(metrics.response_size)

            # Histogram metrics.
            self.extract_session_control_rate_ratio.labels(content_type=self._content_type.value).observe(metrics.session_control_rate)
            self.extract_session_control_concurrency.labels(content_type=self._content_type.value).observe(metrics.session_control_concurrency)
            self.extract_duration_seconds.labels(content_type=self._content_type.value).observe(metrics.duration)
            self.extract_latency_average_seconds.labels(content_type=self._content_type.value).observe(metrics.latency_average)
            self.extract_speedup_ratio.labels(content_type=self._content_type.value).observe(metrics.speedup)
            self.extract_throughput_ratio.labels(content_type=self._content_type.value).observe(metrics.throughput)
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}", exc_info=True)

