#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/metrics/transform.py                                    #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday August 15th 2024 04:31:15 pm                                               #
# Modified   : Sunday August 25th 2024 12:11:46 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Asynchronous Response Metrics Module"""
import sys
import time
from dataclasses import dataclass

import numpy as np

from appstorestream.application.base.metrics import (
    JobMetrics,
    TaskMetrics,
    TransformMetrics,
)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class TransformTaskMetrics(TaskMetrics, TransformMetrics):
    level: str = "task"

    def start(self) -> None:
        self.runtime_start_timestamp_seconds = time.time()

    def stop(self) -> None:
        self.runtime_stop_timestamp_seconds = time.time()
        self.runtime_response_time_seconds = (
            self.runtime_stop_timestamp_seconds - self.runtime_start_timestamp_seconds
        )
        self._compute_record_metrics()
        self._compute_success_failure_rates()
        self._compute_throttle_metrics()

    def add_record(self, record: dict) -> None:
        self.record_count += 1
        self.record_size_bytes_total += sys.getsizeof(record)

    def log_data_error(self) -> None:
        self.success_failure_data_errors_total += 1

    def _compute_record_metrics(self) -> None:
        # Records per second
        self.record_per_second_ratio = (
            (self.record_count / self.runtime_response_time_seconds)
            if self.runtime_response_time_seconds > 0
            else 0
        )
        # Average Record Size
        self.record_average_size_bytes = (
            self.record_size_bytes_total / self.record_count
        )

    def _compute_success_failure_rates(self) -> None:
        # Data Error Rate
        self.success_failure_data_error_rate_ratio = (
            (self.success_failure_data_errors_total / self.record_count)
            if self.record_count > 0
            else 0
        )

        # Success Rate
        self.success_failure_record_success_rate_ratio = (
            1 - self.success_failure_data_error_rate_ratio
        )


# ------------------------------------------------------------------------------------------------ #
@dataclass
class TransformJobMetrics(JobMetrics, TransformMetrics):
    level: str = "job"

    def update_metrics(self, task_metrics: TransformTaskMetrics) -> None:
        self._update_runtime_metrics(task_metrics=task_metrics)
        self._update_record_metrics(task_metrics=TaskMetrics)
        self._update_success_failure_metrics(task_metrics=task_metrics)

    def _update_runtime_metrics(self, task_metrics: TransformTaskMetrics) -> None:
        # Set start timestamp if not already set
        self.runtime_start_timestamp_seconds = (
            self.runtime_start_timestamp_seconds
            or task_metrics.runtime_start_timestamp_seconds
        )
        # Set stop timestamp as a checkpoint
        self.runtime_stop_timestamp_seconds = (
            task_metrics.runtime_stop_timestamp_seconds
        )
        # Set response_time
        self.runtime_response_time_seconds += task_metrics.runtime_response_time_seconds

    def _update_record_metrics(self, task_metrics: TransformTaskMetrics) -> None:
        # Record count
        self.record_count += task_metrics.record_count
        # Total Record Size
        self.record_size_bytes_total += task_metrics.record_size_bytes_total
        # Average Record Size
        self.record_average_size_bytes = (
            self.record_size_bytes_total / self.record_count
        )
        # Records processed per second
        self.record_per_second_ratio = (
            self.record_count / self.runtime_response_time_seconds
        )

    def _update_success_failure_metrics(
        self, task_metrics: TransformTaskMetrics
    ) -> None:
        # Data Errors
        self.success_failure_data_errors_total += (
            task_metrics.success_failure_data_errors_total
        )
        # Data Error Rate
        self.success_failure_data_error_rate_ratio = (
            self.success_failure_data_errors_total / self.record_count
        )
        # Success rate
        self.success_failure_record_success_rate_ratio = (
            1 - self.success_failure_data_error_rate_ratio
        )
