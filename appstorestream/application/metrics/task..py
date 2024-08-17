#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/metrics/task..py                                        #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday August 15th 2024 04:31:15 pm                                               #
# Modified   : Saturday August 17th 2024 02:41:48 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Asynchronous Response Metrics Module"""
import sys
import time
from dataclasses import dataclass, field

import aiohttp
import numpy as np
from prometheus_client import Counter, Gauge

from appstorestream.core.metrics import Metrics, MetricsExporter


# ------------------------------------------------------------------------------------------------ #
@dataclass
class TaskMetrics(Metrics):
    runtime_start_timestamp_seconds: float = 0.0
    runtime_stop_timestamp_seconds: float = 0.0
    runtime_duration_seconds: int = 0

    record_count_total: int = 0
    record_per_second_ratio: float = 0.0

    def start(self) -> None:
        self.runtime_start_timestamp_seconds = time.time()

    def stop(self) -> None:
        self.runtime_stop_timestamp_seconds = time.time()
        self.runtime_duration_seconds = (
            self.runtime_stop_timestamp_seconds - self.runtime_start_timestamp_seconds
        )
        self._compute_record_metrics()

    def add_record(self, record: dict) -> None:
        self.record_count_total += 1

    def _compute_record_metrics(self) -> None:
        # Records per second
        self.record_per_second_ratio = (
            (self.record_count_total / self.runtime_duration_seconds)
            if self.runtime_duration_seconds > 0
            else 0
        )


# ------------------------------------------------------------------------------------------------ #
class TaskMetricsExporter(MetricsExporter):
    """Task Metric Server Class"""

    def __init__(self, job_id: str, dataset: str, port: int = 8000):
        super().__init__(job_id, dataset, port)
        self.define_metrics()

    def define_metrics(self):
        """Defines the metrics for the task process."""

        # Runtime metrics
        self.task_runtime_start_timestamp_seconds = Counter(
            "appstorestream_task_runtime_start_timestamp_seconds",
            "Start timestamp in seconds",
            self._labels.keys(),
        )
        self.task_runtime_stop_timestamp_seconds = Counter(
            "appstorestream_task_runtime_stop_timestamp_seconds",
            "Stop timestamp in seconds",
            self._labels.keys(),
        )
        self.task_runtime_duration_seconds = Gauge(
            "appstorestream_task_runtime_duration_seconds",
            "Runtime in seconds",
            self._labels.keys(),
        )
        self.task_runtime_duration_seconds_total = Counter(
            "appstorestream_task_runtime_duration_seconds_total",
            "Total runtime in seconds",
            self._labels.keys(),
        )

        # Record metrics
        self.task_record_count_total = Counter(
            "appstorestream_task_record_count_total",
            "Total number of records.",
            self._labels.keys(),
        )
        self.task_record_per_second_ratio = Counter(
            "appstorestream_task_record_per_second_ratio",
            "Records processed per second",
            self._labels.keys(),
        )

    def update_metrics(self, metrics):
        """Update the metrics with the provided values."""

        metrics = metrics.as_dict()

        # Update the metrics with the provided values
        self.task_runtime_start_timestamp_seconds.labels(**self._labels).set(
            metrics.get("runtime_start_timestamp_seconds", 0)
        )
        self.task_runtime_stop_timestamp_seconds.labels(**self._labels).set(
            metrics.get("runtime_stop_timestamp_seconds", 0)
        )
        self.task_runtime_duration_seconds.labels(**self._labels).set(
            metrics.get("runtime_duration_seconds", 0)
        )
        self.task_runtime_duration_seconds_total.labels(**self._labels).inc(
            metrics.get("runtime_duration_seconds", 0)
        )

        self.task_record_count_total.labels(**self._labels).inc(
            metrics.get("record_count_total", 0)
        )
        self.task_record_per_second_ratio.labels(**self._labels).inc(
            metrics.get("record_per_second_ratio", 0)
        )
