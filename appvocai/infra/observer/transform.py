#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/observer/transform.py                                               #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 08:53:14 pm                                               #
# Modified   : Thursday September 5th 2024 06:58:07 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Extract Observer Module"""
import logging

from prometheus_client import Gauge, Histogram

from appvocai.application.observer.base import Observer
from appvocai.core.enum import DataType
from appvocai.infra.operator.transform.metrics import MetricsTransform

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------ #
class ObserverTransformMetrics(Observer[MetricsTransform]):
    """
    Observer class for updating transform-related Prometheus metrics.
    """

    def __init__(self, data_type: DataType):
        super().__init__(data_type)

    def _setup_metrics(self) -> None:
        """
        Sets up the Prometheus metrics specific to the transform task.
        """

        # Gauge Metrics
        self.transform_errors_total = Gauge(
            "appvocai_transform_errors_total",
            "Number Of Errors In Transform Step",
            ["data_type"],
        )
        self.transform_records_in_total = Gauge(
            "appvocai_transform_records_in_total",
            "Number Of Transform Input Records",
            ["data_type"],
        )
        self.transform_records_out_total = Gauge(
            "appvocai_transform_records_out_total",
            "Number Of Transform Output Records",
            ["data_type"],
        )

        # Histogram Metrics
        self.transform_duration_seconds = Histogram(
            "appvocai_transform_duration_seconds",
            "Duration Of Transform Step",
            ["data_type"],
        )
        self.transform_throughput_ratio = Histogram(
            "appvocai_transform_throughput_ratio",
            "Ratio Of Number Of Records And Duration",
            ["data_type"],
        )

    def notify(self, metrics: MetricsTransform) -> None:
        """
        Updates the Prometheus metrics with data from a MetricsTransform object.

        Args:
            metrics (MetricsTransform): The transform metrics object containing the data to be updated.
        """
        # Validate the metrics.
        metrics.validate()
        try:
            # Update Gauges
            self.transform_errors.labels(data_type=self._data_type.value).set(
                metrics.errors
            )
            self.transform_records_in.labels(data_type=self._data_type.value).set(
                metrics.records_in
            )
            self.transform_records_out.labels(data_type=self._data_type.value).set(
                metrics.records_out
            )

            # Update Histograms
            self.transform_duration_seconds.labels(
                data_type=self._data_type.value
            ).observe(metrics.duration)
            self.transform_throughput_ratio.labels(
                data_type=self._data_type.value
            ).observe(metrics.throughput)

        except Exception as e:
            logger.error(f"Failed to update metrics: {e}", exc_info=True)
