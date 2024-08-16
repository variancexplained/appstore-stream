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
# Modified   : Friday August 16th 2024 04:37:33 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Metrics Module"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from threading import Lock

from prometheus_client import start_http_server

from appstorestream.core.data import DataClass


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

    def __init__(self, job_id: str, dataset: str, port: int = 8000):
        self.start_server(port=port)
        self._labels = {"job_id": job_id, "dataset": dataset}

    @classmethod
    def start_server(cls, port: int = 8000):
        with cls._lock:
            if not cls._server_started:
                start_http_server(port)
                cls._server_started = True

    @abstractmethod
    def define_metrics(self):
        """Specifies a method to initialize at the beginning of a process."""

    @abstractmethod
    def update_metrics(self, metrics: Metrics) -> None:
        """Specifies a method to initialize at the beginning of a process."""
