#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/base/response.py                                        #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 03:50:26 am                                                   #
# Modified   : Sunday July 28th 2024 05:20:37 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Application Layer Base Module"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
from aiohttp import ClientResponseError

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
    content = List[Dict[str,Any]]
    time_sent: datetime = None
    time_recv: datetime = None
    concurrent_requests_duration:  int = 0
    request_count: int = 0
    response_count: int = 0
    record_count: int = 0
    throughput: float = 0
    total_errors: int = 0
    redirect_errors: int = 0
    client_errors: int = 0
    server_errors: int = 0
    data_errors: int = 0
    unknown_errors: int = 0
    page_not_found_errors: int = 0


    def get_content(self) -> pd.DataFrame:
        """Returns the content from the AsyncRequest as a pandas dictionary"""
        return pd.DataFrame(self.content)

    def send(self) -> None:
        self.time_sent = datetime.now()

    def recv(self, results: list) -> None:
        self.time_recv = datetime.now()
        self.concurrent_requests_duration = (self.time_recv-self.time_sent).total_seconds()
        self.parse_results(results=results)
        self.throughput = self.record_count / self.concurrent_requests_duration

    def log_error(self, error: ResponseError) -> None:
        self.total_errors += 1
        if 'redirect' in error.error_type.lower():
            self.redirect_errors += 1
        elif 'client' in error.error_type.lower():
            self.client_errors += 1
        elif 'server' in error.error_type.lower():
            self.server_errors += 1
        else:
            self.unknown_errors += 1
        if error.return_code == 404:
            self.page_not_found_errors += 1

    def get_logger(self) -> logging.Logger:
        return logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def parse_results(self, results: list) -> None:
        """Parse the results"""

