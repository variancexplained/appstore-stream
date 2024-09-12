#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /acquire/application/stage/base.py                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 04:22:03 pm                                              #
# Modified   : Monday September 9th 2024 04:57:55 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from abc import ABC, abstractmethod
from typing import Optional

from acquire.core.enum import StageType
from acquire.domain.artifact.base import Artifact


# ------------------------------------------------------------------------------------------------ #
class Stage(ABC):
    """Abstract base class for Task objects."""

    @property
    @abstractmethod
    def stage(self) -> StageType:
        """Extract, Transform or Load"""

    @abstractmethod
    def run(self, artifact: Artifact) -> Optional[Artifact]:
        """Executes the task."""
