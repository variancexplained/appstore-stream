#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/metrics/task.py                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday August 15th 2024 11:26:23 pm                                               #
# Modified   : Friday August 16th 2024 04:23:52 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import time
from dataclasses import dataclass

from prometheus_client import Counter, Gauge

from appstorestream.core.metrics import Metrics, MetricServer


# ------------------------------------------------------------------------------------------------ #
@dataclass
class TaskMetrics(Metrics):
    start: float = 0.0
    stop: float = 0.0
    runtime_seconds: float = 0.0
    sessions_total: int = 0
    records_total: int = 0
    records_per_second_ratio: float = 0

    def start(self) -> None:
        self.start = time.time()

    def stop(self) -> None:
        self.stop = time.time()
        self.runtime_seconds = self.stop - self.start
        self.records_per_second_ratio = self.records_total / self.runtime_seconds

    def update_metrics(self, metrics: Metrics) -> None:
        self.sessions_total += 1
        self.records_total += metrics.session_records_total


# ------------------------------------------------------------------------------------------------ #
class TaskMetricServer(MetricServer):
    """Task Metric Server Class"""

    def __init__(self, job_id: str, dataset: str, port: int = 8000):
        super().__init__(job_id, dataset, port)
        self.define_metrics()

    def define_metrics(self):
        """Defines the metrics for the task."""

        # Define the metrics
        self.runtime_seconds_total = Counter(
            "appstorestream_runtime_seconds",
            "Total runtime in seconds",
            self._labels.keys(),
        )
        self.sessions_total = Counter(
            "appstorestream_sessions_total",
            "Total number of sessions",
            self._labels.keys(),
        )
        self.records_total = Counter(
            "appstorestream_records_total",
            "Total number of records processed",
            self._labels.keys(),
        )
        self.records_per_second_ratio = Gauge(
            "appstorestream_records_per_second_ratio",
            "Records processed per second",
            self._labels.keys(),
        )

    def update_metrics(self, metrics: Metrics):
        """Update the metrics with the provided values."""

        # Update the metrics with the provided values
        # Converting`metrics` to a dictionary containing the new values
        metrics = metrics.ad_dict()
        self.runtime_seconds_total.labels(**self._labels).inc(
            metrics.get("runtime_seconds", 0)
        )
        self.sessions_total.labels(**self._labels).inc(metrics.get("sessions_total", 0))
        self.records_total.labels(**self._labels).inc(metrics.get("records_total", 0))
        self.records_per_second_ratio.labels(**self._labels).set(
            metrics.get("records_per_second_ratio", 0)
        )
