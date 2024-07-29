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
# Modified   : Monday July 29th 2024 03:54:51 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Application Layer Base Module"""
import logging
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from appstorestream.core.data import DataClass
from appstorestream.core.enum import ErrorType


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ResponseError(DataClass):
    """Encapsulates the response error that is returned once retries are exhaused."""

    return_code: int
    error_type: ErrorType = None

    def __post_init__(self) -> None:
        if 300 <= self.return_code < 400:
            self.error_type = "RedirectError"
        if 400 <= self.return_code < 500:
            self.error_type = "ClientResponseError"
        elif 500 <= self.return_code < 600:
            self.error_type = "ServerResponseError"
        else:
            self.error_type = "Unknown"


# ------------------------------------------------------------------------------------------------ #
@dataclass
class AsyncResponse(DataClass):
    content: list[dict] = field(default_factory=list)
    time_sent: datetime = None
    time_recv: datetime = None
    concurrent_requests_duration: int = 0
    request_count: int = 0
    response_count: int = 0
    record_count: int = 0
    request_throughput: float = 0.0
    response_throughput: float = 0.0
    record_throughput: float = 0.0
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
    ok: bool = False

    def get_content(self) -> pd.DataFrame:
        """Returns the content from the AsyncRequest as a pandas dictionary"""
        return pd.DataFrame(self.content)

    def send(self) -> None:
        self.time_sent = datetime.now()

    def recv(self, results: list) -> None:
        self.time_recv = datetime.now()
        self.concurrent_requests_duration = (
            self.time_recv - self.time_sent
        ).total_seconds()
        self.parse_results(results=results)

        self.request_throughput = self.request_count / self.concurrent_requests_duration
        self.response_throughput = (
            self.response_count / self.concurrent_requests_duration
        )
        self.record_throughput = self.record_count / self.concurrent_requests_duration

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

        self.ok = len(self.content) > 0

    def log_error(self, error: ResponseError) -> None:
        self.total_errors += 1
        if "redirect" in error.error_type.lower():
            self.redirect_errors += 1
        elif "client" in error.error_type.lower():
            self.client_errors += 1
        elif "server" in error.error_type.lower():
            self.server_errors += 1
        else:
            self.unknown_errors += 1
        if error.return_code == 404:
            self.page_not_found_errors += 1

    @abstractmethod
    def parse_results(self, results: list) -> None:
        """Parse the results"""
