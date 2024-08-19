#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/base/metrics.py                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 17th 2024 01:26:17 pm                                               #
# Modified   : Saturday August 17th 2024 06:16:22 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Application Metrics Base Class Module"""
from __future__ import annotations

from dataclasses import dataclass

from appstorestream.core.data import DataClass


# ------------------------------------------------------------------------------------------------ #
@dataclass
class JobMetrics(DataClass):
    def update_metrics(self, task_metrics: TaskMetrics) -> None:
        """Updates the job metrics based upon task_metrics"""


# ------------------------------------------------------------------------------------------------ #
@dataclass
class TaskMetrics(DataClass):
    def start(self) -> None:
        """Metrics to be initialized at the start of a monitored process"""

    def stop(self) -> None:
        """Metrics to be initialized at the end of a monitored process"""


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ExtractMetrics(DataClass):
    category: str = "extract"
    level: str = None  # Either 'job', or 'task'. Defined in subclasses.
    runtime_start_timestamp_seconds: float = 0.0
    runtime_stop_timestamp_seconds: float = 0.0
    runtime_duration_seconds: float = 0.0
    request_count_total: int = 0
    request_per_second_ratio: float = 0.0
    response_count_total: int = 0
    response_per_second_ratio: float = 0.0
    response_average_latency_seconds: float = 0.0
    response_latency_seconds_total: float = 0.0
    response_average_size_bytes: int = 0
    response_size_bytes_total: int = 0
    success_failure_retries_total: int = 0
    success_failure_errors_total: int = 0
    success_failure_client_errors_total: int = 0
    success_failure_server_errors_total: int = 0
    success_failure_redirect_errors_total: int = 0
    success_failure_unknown_errors_total: int = 0
    success_failure_request_failure_rate_ratio: float = 0.0
    success_failure_request_success_rate_ratio: float = 0.0


# ------------------------------------------------------------------------------------------------ #
@dataclass
class TransformMetrics(DataClass):
    category: str = "transform"
    level: str = None  # Either 'job', or 'task'. Defined in subclasses.
    runtime_start_timestamp_seconds: float = 0.0
    runtime_stop_timestamp_seconds: float = 0.0
    runtime_duration_seconds: float = 0.0
    record_count: int = 0
    record_size_bytes_total: int = 0
    record_average_size_bytes: int = 0
    record_per_second_ratio: float = 0.0
    success_failure_data_errors_total: int = 0
    success_failure_data_error_rate_ratio: int = 0
    success_failure_record_success_rate_ratio: float = 0.0


# ------------------------------------------------------------------------------------------------ #
@dataclass
class LoadMetrics(DataClass):
    category: str = "load"
    level: str = None  # Either 'job', or 'task'. Defined in subclasses.
    runtime_start_timestamp_seconds: float = 0.0
    runtime_stop_timestamp_seconds: float = 0.0
    runtime_duration_seconds: float = 0.0
    record_count: int = 0
    record_average_size_bytes: int = 0
    record_size_bytes_total: int = 0
    record_per_second_ratio: float = 0.0
