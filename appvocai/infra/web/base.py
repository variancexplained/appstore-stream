#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/web/base.py                                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 08:20:44 am                                                   #
# Modified   : Tuesday September 3rd 2024 12:39:26 pm                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Web Infrastructure Base Module"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict


# ------------------------------------------------------------------------------------------------ #
class Header(ABC):
    """Interface for classes that serve up HTTP Headers."""

    @abstractmethod
    def __iter__(self) -> Header:
        """Initializes the iteration"""

    @abstractmethod
    def __next__(self) -> Dict[str,str]:
        """Returns a randomly selected header."""
