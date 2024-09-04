#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/observer/error.py                                                   #
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
"""Error Observer Module"""
import logging

from prometheus_client import Counter

from appvocai.core.enum import ContentType
from appvocai.infra.observer.base import Observer

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------ #
class ObserverTransformMetrics(Observer):
    """
    Observer class for updating transform-related Prometheus metrics.
    """

    def __init__(self, content_type: ContentType):
        super().__init__(content_type)

    def _setup_metrics(self) -> None:
        """
        Sets up the Prometheus metrics specific to the transform task.
        """

        # Gauge Metrics
        self.errors_total = Counter(
            "appvocai_transform_errors_total",
            "Number Of Errors In Transform Step",
            ["content_type"],
        )
        self.transform_records_in_total = Gauge(
            "appvocai_transform_records_in_total",
            "Number Of Transform Input Records",
            ["content_type"],
        )
        self.transform_records_out_total = Gauge(
            "appvocai_transform_records_out_total",
            "Number Of Transform Output Records",
            ["content_type"],
        )

        # Histogram Metrics
        self.transform_duration_seconds = Histogram(
            "appvocai_transform_duration_seconds",
            "Duration Of Transform Step",
            ["content_type"],
        )
        self.transform_throughput_ratio = Histogram(
            "appvocai_transform_throughput_ratio",
            "Ratio Of Number Of Records And Duration",
            ["content_type"],
        )

    def notify(self, subject: str, error_code: Op) -> None:
        """
        Updates the Prometheus metrics with data from a MetricsTransform object.

        Args:
            metrics (MetricsTransform): The transform metrics object containing the data to be updated.
        """
        # Validate the metrics.
        metrics.validate()
        try:
            # Update Gauges
            self.transform_errors.labels(content_type=self._content_type.value).set(
                metrics.errors
            )
            self.transform_records_in.labels(content_type=self._content_type.value).set(
                metrics.records_in
            )
            self.transform_records_out.labels(
                content_type=self._content_type.value
            ).set(metrics.records_out)

            # Update Histograms
            self.transform_duration_seconds.labels(
                content_type=self._content_type.value
            ).observe(metrics.duration)
            self.transform_throughput_ratio.labels(
                content_type=self._content_type.value
            ).observe(metrics.throughput)

        except Exception as e:
            logger.error(f"Failed to update metrics: {e}", exc_info=True)
