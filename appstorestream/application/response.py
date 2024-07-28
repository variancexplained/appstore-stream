#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/response.py                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 03:50:26 am                                                   #
# Modified   : Saturday July 27th 2024 02:22:54 am                                                 #
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


# ------------------------------------------------------------------------------------------------ #
@dataclass
class AsyncResponse(DataClass):
    content = List[Dict[str,Any]]
    errors: list = []
    time_sent: datetime = None
    time_recv: datetime = None
    runtime:  int = 0
    request_count: int = 0
    app_count: int = 0
    review_count: int = 0
    request_throughput: float = 0
    app_throughput: float = 0
    total_latency: float = 0
    ave_latency: float = 0
    total_errors: float = 0
    client_errors: float = 0
    server_errors: float = 0
    data_errors: float = 0
    data_errors  : int = 0

    def send(self) -> None:
        self.sent = datetime.now()

    def recv(self, response: list) -> None:
        self.recv = datetime.now()
        self.total_latency += (self.recv-self.sent).total_seconds()
        self.ave_latency = self.total_latency / len(response)
        self.parse_response(response)

    @property
    def content(self) -> pd.DataFrame:
        """Returns the content from the AsyncRequest as a pandas dictionary"""
        return pd.DataFrame(self._content)

    @property
    def errors(self) -> list:
        """Returns the errors from the request."""
        return self._errors

    def check_response_code(self, error: ClientResponseError) -> bool:
        """Evaluates the status code from the ClientResponseError object and updates stats accordingly."""
        status_code = int(error.status)
        if status_code == 200:
             return True
        elif status_code > 299 and status_code < 400:
             self.server_errors += 1
             self.total_errors += 1
             self.errors.append(error)
             return False
        elif status_code > 399 and status_code < 500:
             self.client_errors += 1
             self.total_errors += 1
             self.errors.append(error)
             return False
        elif status_code > 499:
             self.server_errors += 1
             self.total_errors += 1
             self.errors.append(error)
             return False

    @abstractmethod
    def parse_response(self) -> None:
        """Parse the response"""

