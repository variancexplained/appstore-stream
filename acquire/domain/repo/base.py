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
# Modified   : Thursday August 29th 2024 08:22:41 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Job Repo Module"""
from abc import ABC, abstractmethod
from typing import Any


# ------------------------------------------------------------------------------------------------ #
class Repo(ABC):
    """Base class for application layer repositories.

    This class serves as an abstract base class for repositories.
    """

    @abstractmethod
    def get(self, id_value: int) -> Any:
        """Fetches an entity by its ID."""
        pass
