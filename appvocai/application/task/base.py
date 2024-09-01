#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/task/base.py                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 04:22:03 pm                                              #
# Modified   : Sunday September 1st 2024 01:07:59 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from abc import ABC, abstractmethod
from typing import Awaitable, Generic, TypeVar

from appvocai.domain.response.base import ResponseAsync

# ------------------------------------------------------------------------------------------------ #
T = TypeVar('T')
# ------------------------------------------------------------------------------------------------ #
class Task(ABC, Generic[T]):
    """Abstract base class for Task objects."""

    @abstractmethod
    def run(self, async_request: T) -> Awaitable[ResponseAsync]:
        """Executes the task."""

