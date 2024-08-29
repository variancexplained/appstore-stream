#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/repo/base.py                                                       #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday August 29th 2024 02:48:02 am                                               #
# Modified   : Thursday August 29th 2024 06:49:14 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Job Repo Module"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# ------------------------------------------------------------------------------------------------ #
T = TypeVar('T')
# ------------------------------------------------------------------------------------------------ #
class Repo(ABC, Generic[T]):
    """Base class for application layer repositories.

    This class serves as an abstract base class for repositories.
    """

    @abstractmethod
    def get(self, id_value: int) -> T:
        """Fetches an entity by its ID."""
        pass
