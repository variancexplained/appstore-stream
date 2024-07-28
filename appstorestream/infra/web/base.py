#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoC: AppStore Voice of the Customer                                              #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvoc/infrastructure/web/base.py                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvoc                                          #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 04:43:24 am                                                   #
# Modified   : Monday July 22nd 2024 04:45:25 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Web Infrastructure Base Module"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod


# ------------------------------------------------------------------------------------------------ #
class Throttle(ABC):
    """Base class for HTTP request rate limiters"""

    def __init__(self) -> None:
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    @abstractmethod
    def delay(self, *args, **kwargs) -> int:
        """Returns a delay time in milliseconds"""
