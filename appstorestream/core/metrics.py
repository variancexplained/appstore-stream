#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/core/metrics.py                                                     #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday July 29th 2024 06:13:17 pm                                                   #
# Modified   : Saturday August 17th 2024 12:43:35 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Metrics Module"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from threading import Lock

from prometheus_client import CollectorRegistry, Counter, Gauge, start_http_server

from appstorestream.core.data import DataClass
from appstorestream.infra.base.config import Config


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Metrics(DataClass):
    """Base Metrics class"""

    @abstractmethod
    def start(self) -> None:
        """Abstract method to capture metrics at process start."""

    @abstractmethod
    def stop(self) -> None:
        """Abstract method to capture metrics at process stop."""


# ------------------------------------------------------------------------------------------------ #
class MetricsExporter(ABC):
    """Base Metric Server Class"""

    _server_started = False
    _lock = Lock()

    def __init__(
        self,
        job_id: str,
        dataset: str,
        config_cls: type[Config] = Config,
        registry: CollectorRegistry = None,
        port: int = 8000,
    ):
        self._config = config_cls()
        self._registry = registry or CollectorRegistry()
        self.start_server(port=port)
        self.labels = {"job_id": job_id, "dataset": dataset}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def get_or_create_metric(self, metric_name, metric_type, description, labels):
        """Utility method to get or create a metric."""
        try:
            # Try creating and registering the metric
            if metric_type == "Counter":
                self._logger.debug(f"Creating Counter metric {metric_name}")
                return Counter(
                    metric_name, description, labels, registry=self._registry
                )
            elif metric_type == "Gauge":
                self._logger.debug(f"Creating Gauge metric {metric_name}")
                return Gauge(metric_name, description, labels, registry=self._registry)
            else:
                raise ValueError(f"Unsupported metric type: {metric_type}")
        except ValueError as e:
            if "Duplicated timeseries" in str(e):
                self._logger.debug(f"Duplicate timeseries found for {metric_name}.")
                # Metric already exists, retrieve it from the registry
                for metric_family in self._registry.collect():
                    for sample in metric_family.samples:
                        if sample.name == metric_name:
                            # Return the metric that caused the duplicate error
                            for collector in self._registry._collector_to_names:
                                if (
                                    metric_name
                                    in self._registry._collector_to_names[collector]
                                ):
                                    self._logger.debug(
                                        f"Found existing metric: {metric_name}"
                                    )
                                    return collector
                msg = f"Unable to retrieve metric {metric_name} from the registry."
                raise RuntimeError(msg)

            else:
                raise

    def load_config(self, category: str, level: str) -> list:
        return self._config.load_metrics_config()

    @classmethod
    def start_server(cls, port: int = 8000):
        with cls._lock:
            if not cls._server_started:
                start_http_server(port)
                cls._server_started = True

    @abstractmethod
    def define_metrics(self) -> None:
        """Defines the metrics scraped by prometheus."""

    @abstractmethod
    def update_metrics(self, metrics: Metrics) -> None:
        """Updates the metrics."""
