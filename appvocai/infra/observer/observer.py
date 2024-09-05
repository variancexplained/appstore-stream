#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/observer/observer.py                                                #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 08:53:14 pm                                               #
# Modified   : Thursday September 5th 2024 04:57:03 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Error Observer Module"""
import logging
from typing import TypeVar

from prometheus_client import Counter

from appvocai.core.enum import DataType
from appvocai.infra.monitor.metrics import Metrics
from appvocai.infra.observer.base import Observer
from appvocai.infra.operator.error.metrics import MetricsError

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------ #
T = TypeVar("T", bound=Metrics)


# ------------------------------------------------------------------------------------------------ #
class ObserverError(Observer[MetricsError]):
    """
    Observer class for updating transform-related Prometheus metrics.
    """

    def __init__(self, data_type: DataType):
        self._data_type = data_type
        self._setup_metrics()

    def _setup_metrics(self) -> None:
        """
        Sets up the Prometheus metrics specific to the transform task.
        """

        # Gauge Metrics
        self.errors_total = Counter(
            "appvocai_errors_total",
            "Number Of Errors",
            ["data_type", "error_type", "operator"],
        )

    def notify(self, metrics: MetricsError) -> None:
        """
        Updates the Prometheus metrics with data from a MetricsTransform object.

        Args:
            metrics (MetricsTransform): The transform metrics object containing the data to be updated.
        """
        # Validate the metrics.
        metrics.validate()
        try:
            self.errors_total.labels(
                data_type=self._data_type.value,
                error_type=metrics.error_type.value,
                operator=metrics.operator,
            ).inc()

        except Exception as e:
            logger.error(f"Failed to update metrics: {e}", exc_info=True)
