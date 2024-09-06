#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/operation/base.py                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 04:22:03 pm                                              #
# Modified   : Friday September 6th 2024 03:56:36 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from abc import ABC, abstractmethod
from typing import Any

from appvocai.core.enum import OperationType


# ------------------------------------------------------------------------------------------------ #
class Operation(ABC):
    """Abstract base class for Task objects."""

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Executes the task."""

    @abstractmethod
    def operation_type(self) -> OperationType:
        """An OperationType Enum value, EXTRACT, TRANSFORM, or LOAD"""
