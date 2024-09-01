#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/observer/base.py                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 08:52:56 pm                                               #
# Modified   : Sunday September 1st 2024 12:45:37 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Observer Base Module"""
import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from prometheus_client import start_http_server

from appvocai.core.enum import ContentType
from appvocai.domain.metrics.base import Metrics

# ------------------------------------------------------------------------------------------------ #
T = TypeVar('T', bound='Metrics')
# ------------------------------------------------------------------------------------------------ #
class Observer(ABC, Generic[T]):
    """
    Base class for a metrics observer that starts a Prometheus server and updates metrics.

    This class should be extended by concrete observer classes that handle specific types of metrics.
    It includes a content type to differentiate between different kinds of monitored content.
    """

    def __init__(self, content_type: ContentType, port: int = 8000):
        """
        Initializes the Prometheus server and sets up necessary metrics.

        Args:
            content_type (ContentType): The type of content being observed, used to label or filter metrics.
            port (int): The port on which the Prometheus server should be exposed. Defaults to 8000.
        """
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._content_type = content_type
        self.port = port
        self._start_server()
        self._setup_metrics()

    def _start_server(self) -> None:
        """
        Starts the Prometheus HTTP server on the specified port.
        """
        start_http_server(self.port)
        self._logger.info(f"Prometheus server started on port {self.port}")

    @abstractmethod
    def _setup_metrics(self) -> None:
        """
        Sets up the Prometheus metrics that will be updated by the observer.

        This method should be implemented by subclasses to define the specific metrics.
        """
        pass

    @abstractmethod
    def notify(self, metrics: T) -> None:
        """
        Updates the Prometheus metrics based on the provided Metrics object.

        Args:
            metrics (Metrics): The metrics object containing the data to be updated.
        """
        pass
