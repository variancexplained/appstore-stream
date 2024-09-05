#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/observer/load.py                                                    #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 08:53:14 pm                                               #
# Modified   : Thursday September 5th 2024 06:58:08 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Extract Observer Module"""
import logging

from prometheus_client import Gauge, Histogram

from appvocai.application.observer.base import Observer
from appvocai.core.enum import DataType
from appvocai.domain.metrics.load import MetricsLoad

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------ #
class ObserverLoadMetrics(Observer[MetricsLoad]):
    """
    Observer class for updating load-related Prometheus metrics.
    """

    def __init__(self, data_type: DataType):
        super().__init__(data_type)

    def _setup_metrics(self) -> None:
        """
        Sets up the Prometheus metrics specific to the load task.
        """

        # Gauge Metrics
        self.transform_errors = Gauge(
            "appvocai_load_errors", "Number Of Errors In Load Step", ["data_type"]
        )
        self.transform_records = Gauge(
            "appvocai_load_records", "Number Of Load Records", ["data_type"]
        )

        # Histogram Metrics
        self.transform_duration_seconds = Histogram(
            "appvocai_load_duration_seconds", "Duration Of Load Step", ["data_type"]
        )
        self.transform_throughput_ratio = Histogram(
            "appvocai_load_throughput_ratio",
            "Ratio Of Number Of Records And Duration",
            ["data_type"],
        )

    def notify(self, metrics: MetricsLoad) -> None:
        """
        Updates the Prometheus metrics with data from a MetricsLoad object.

        Args:
            metrics (MetricsLoad): The load metrics object containing the data to be updated.
        """
        # Validate the metrics.
        metrics.validate()
        try:
            # Update Gauges
            self.transform_errors.labels(data_type=self._data_type.value).set(
                metrics.errors
            )
            self.transform_records.labels(data_type=self._data_type.value).set(
                metrics.records
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
