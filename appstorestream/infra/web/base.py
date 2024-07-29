#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/web/base.py                                                   #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 08:20:44 am                                                   #
# Modified   : Monday July 29th 2024 03:42:34 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Web Infrastructure Base Module"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod


# ------------------------------------------------------------------------------------------------ #
class Header(ABC):
    """Interface for classes that serve up HTTP Headers."""

    @abstractmethod
    def __iter__(self):
        """Initializes the iteration"""

    @abstractmethod
    def __next__(self):
        """Returns a randomly selected header."""


# ------------------------------------------------------------------------------------------------ #
class Throttle(ABC):
    """Base class for HTTP request rate limiters"""

    def __init__(self) -> None:
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    @abstractmethod
    def delay(self, *args, **kwargs) -> int:
        """Returns a delay time in milliseconds"""
