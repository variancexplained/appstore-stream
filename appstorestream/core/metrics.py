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
# Modified   : Friday August 16th 2024 09:05:54 pm                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Metrics Module"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from threading import Lock
from typing import Union

from prometheus_client import (
    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    start_http_server,
)

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
class MetricServer(ABC):
    """Base Metric Server Class"""

    _server_started = False
    _lock = Lock()

    def __init__(
        self,
        job_id: str,
        dataset: str,
        config_cls: type[Config] = Config,
        registry: CollectorRegistry = REGISTRY,
        port: int = 8000,
    ):
        self._config = config_cls()
        self._registry = registry
        self.start_server(port=port)
        self.labels = {"job_id": job_id, "dataset": dataset}

    def get_or_create_metric(self, metric_name, metric_type, description, labels):
        """Utility function to get or create a metric."""
        try:
            if metric_type == "Counter":
                return Counter(
                    metric_name, description, labels, registry=self._registry
                )
            elif metric_type == "Gauge":
                return Gauge(metric_name, description, labels, registry=self._registry)
            else:
                raise ValueError(f"Unsupported metric type: {metric_type}")
        except ValueError as e:
            if "Duplicated timeseries" in str(e):
                # Retrieve existing metric from the registry if it already exists
                for collector in self._registry.collectors:
                    for metric in collector.collect():
                        if metric.name == metric_name:
                            return collector
            else:
                raise

    def load_config(self, category: str) -> list:
        return self._config.load_metrics_config()[category]

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
