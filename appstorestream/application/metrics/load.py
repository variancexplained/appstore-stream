#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/metrics/load.py                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday August 15th 2024 04:31:15 pm                                               #
# Modified   : Friday August 16th 2024 11:43:47 am                                                 #
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

from appstorestream.core.metrics import Metrics, MetricServer


# ------------------------------------------------------------------------------------------------ #
@dataclass
class LoadMetrics(Metrics):
    runtime_start_timestamp_seconds: float = None
    runtime_stop_timestamp_seconds: float = None
    runtime_duration_seconds: float = None

    record_count: int = None
    record_size_bytes: int = None
    record_per_second_ratio: float = None

    def start(self) -> None:
        self.runtime_start_timestamp_seconds = time.time()

    def stop(self) -> None:
        self.runtime_stop_timestamp_seconds = time.time()
        self.runtime_duration_seconds = (
            self.runtime_stop_timestamp_seconds - self.runtime_start_timestamp_seconds
        )
        self._compute_record_metrics()

    def add_record(self, record: dict) -> None:
        self.record_count += 1
        self.record_size_bytes += sys.getsizeof(record)

    def _compute_record_metrics(self) -> None:
        # Records per second
        self.record_per_second_ratio = (
            (self.record_count / self.runtime_duration_seconds)
            if self.runtime_duration_seconds > 0
            else 0
        )


# ------------------------------------------------------------------------------------------------ #
class LoadMetricServer(MetricServer):
    """Load Metric Server Class"""

    def __init__(self, job_id: str, dataset: str, port: int = 8000):
        super().__init__(job_id, dataset, port)
        self.define_metrics()

    def define_metrics(self):
        """Defines the metrics for the load process."""

        # Runtime metrics
        self.load_runtime_start_timestamp_seconds = Counter(
            "appstorestream_load_runtime_start_timestamp_seconds",
            "Start timestamp in seconds",
            self._labels.keys(),
        )
        self.load_runtime_stop_timestamp_seconds = Counter(
            "appstorestream_load_runtime_stop_timestamp_seconds",
            "Stop timestamp in seconds",
            self._labels.keys(),
        )
        self.load_runtime_duration_seconds = Gauge(
            "appstorestream_load_runtime_duration_seconds",
            "Duration in seconds",
            self._labels.keys(),
        )
        self.load_runtime_duration_seconds_total = Counter(
            "appstorestream_load_runtime_duration_seconds_total",
            "Total duration in seconds",
            self._labels.keys(),
        )

        # Record metrics
        self.load_record_count = Gauge(
            "appstorestream_load_record_count", "Load record count", self._labels.keys()
        )
        self.load_record_count_total = Counter(
            "appstorestream_load_record_count_total",
            "Total load record count",
            self._labels.keys(),
        )
        self.load_record_size_bytes = Gauge(
            "appstorestream_load_record_size_bytes",
            "Load record size in bytes",
            self._labels.keys(),
        )
        self.load_record_size_bytes_total = Counter(
            "appstorestream_load_record_size_bytes_total",
            "Total load record size in bytes",
            self._labels.keys(),
        )
        self.load_record_per_second_ratio = Gauge(
            "appstorestream_load_record_per_second_ratio",
            "Records per second",
            self._labels.keys(),
        )

    def update_metrics(self, metrics):
        """Update the metrics with the provided values."""

        metrics = metrics.as_dict()

        # Update the metrics with the provided values
        self.load_runtime_start_timestamp_seconds.labels(**self._labels).set(
            metrics.get("runtime_start_timestamp_seconds", 0)
        )
        self.load_runtime_stop_timestamp_seconds.labels(**self._labels).set(
            metrics.get("runtime_stop_timestamp_seconds", 0)
        )
        self.load_runtime_duration_seconds.labels(**self._labels).set(
            metrics.get("runtime_duration_seconds", 0)
        )
        self.load_runtime_duration_seconds_total.labels(**self._labels).inc(
            metrics.get("runtime_duration_seconds_total", 0)
        )

        self.load_record_count.labels(**self._labels).set(
            metrics.get("record_count", 0)
        )
        self.load_record_count_total.labels(**self._labels).inc(
            metrics.get("record_count", 0)
        )
        self.load_record_size_bytes.labels(**self._labels).set(
            metrics.get("record_size_bytes", 0)
        )
        self.load_record_size_bytes_total.labels(**self._labels).inc(
            metrics.get("record_size_bytes", 0)
        )
        self.load_record_per_second_ratio.labels(**self._labels).set(
            metrics.get("record_per_second_ratio", 0)
        )
