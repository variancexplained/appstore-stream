#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/domain/base/response.py                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 03:50:26 am                                                   #
# Modified   : Wednesday July 31st 2024 04:52:53 am                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Application Layer Base Module"""
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import pandas as pd

from appstorestream.core.data import DataClass


# ------------------------------------------------------------------------------------------------ #
@dataclass
class AsyncResponseMetrics(DataClass):
    time_sent: float = None
    time_recv: float = None
    latency: list[float] = field(default_factory=list)
    average_latency: float = 0.0
    total_latency: float = 0.0
    effective_latency: float = 0.0
    duration: float = 0.0
    average_concurrent_latency: float = 0.0
    concurrency_efficiency_ratio: float = 0.0
    request_count: int = 0
    response_count: int = 0
    record_count: int = 0
    requests_per_second: float = 0.0
    responses_per_second: float = 0.0
    records_per_second: float = 0.0
    total_errors: int = 0
    redirect_errors: int = 0
    client_errors: int = 0
    server_errors: int = 0
    data_errors: int = 0
    unknown_errors: int = 0
    page_not_found_errors: int = 0
    total_error_rate: float = 0.0
    redirect_error_rate: float = 0.0
    client_error_rate: float = 0.0
    server_error_rate: float = 0.0
    data_error_rate: float = 0.0
    unknown_error_rate: float = 0.0
    page_not_found_error_rate: float = 0.0
    retries: int = 0

    def send(self) -> None:
        self.time_sent = time.time()

    def recv(self) -> None:
        self.time_recv = time.time()
        self.duration = self.time_recv - self.time_sent
        self.average_latency = (
            sum(self.latency) / len(self.latency) if len(self.latency) > 0 else 0
        )
        self.total_latency = sum(self.latency)

    def add_latency(self, latency: float) -> None:
        self.latency.append(latency)

    def log_error(self, return_code: int) -> None:
        self.total_errors += 1
        if 300 <= return_code < 400:
            self.redirect_errors += 1
        if 400 <= return_code < 500:
            self.client_errors += 1
            if return_code == 404:
                self.page_not_found_errors += 1
        elif 500 <= return_code < 600:
            self.server_errors += 1
        else:
            self.unknown_errors += 1

    def finalize(self) -> None:

        # Request Throughput Metrics
        self.requests_per_second = (
            self.request_count / self.duration if self.duration > 0 else 0
        )
        self.responses_per_second = (
            self.response_count / self.duration if self.duration > 0 else 0
        )

        self.records_per_second = (
            self.record_count / self.duration if self.duration > 0 else 0
        )

        # Performance Metrics
        self.average_concurrent_latency = (
            self.duration / self.request_count if self.request_count > 0 else 0
        )
        self.concurrency_efficiency_ratio = (
            self.total_latency / (self.request_count * self.duration)
            if self.request_count > 0
            else 0
        )
        self.effective_latency = (
            self.total_latency / self.duration if self.duration > 0 else 0
        )

        # Error Rates
        self.total_error_rate = (
            self.total_errors / self.request_count if self.request_count > 0 else 0
        )
        self.redirect_error_rate = (
            self.redirect_errors / self.request_count if self.request_count > 0 else 0
        )
        self.client_error_rate = (
            self.client_errors / self.request_count if self.request_count > 0 else 0
        )
        self.server_error_rate = (
            self.server_errors / self.request_count if self.request_count > 0 else 0
        )
        self.data_error_rate = (
            self.data_errors / self.request_count if self.request_count > 0 else 0
        )
        self.unknown_error_rate = (
            self.unknown_errors / self.request_count if self.request_count > 0 else 0
        )
        self.page_not_found_error_rate = (
            self.page_not_found_errors / self.request_count
            if self.request_count > 0
            else 0
        )


# ------------------------------------------------------------------------------------------------ #
class AsyncResponse(ABC):
    def __init__(self, results: list, metrics: AsyncResponseMetrics) -> None:
        self._results = results
        self._metrics = metrics
        self._content = []
        self._finalized = False
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def ok(self) -> bool:
        return len(self._content) > 0

    @property
    def metrics(self) -> AsyncResponseMetrics:
        if not self._finalized:
            self._not_finalized()
        else:
            return self._metrics

    @property
    def content(self) -> pd.DataFrame:
        if not self._finalized:
            self._not_finalized()
        else:
            return pd.DataFrame(self._content)

    def process_response(self) -> pd.DataFrame:
        """Returns the content from the AsyncRequest as a pandas dictionary"""
        self.parse_results(results=self._results)
        self._metrics.finalize()
        self._finalized = True

    @abstractmethod
    def parse_results(self, results: list) -> None:
        """Parse the results"""

    def _not_finalized(self) -> None:
        self._logger.warning(
            "The response has not been finalized. Run process_response prior to accessing response content and metrics."
        )
