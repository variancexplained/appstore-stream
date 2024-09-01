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
# Modified   : Saturday August 31st 2024 09:16:50 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Observer Base Module"""
from abc import ABC, abstractmethod

from appvocai.domain.metrics.base import Metrics


# ------------------------------------------------------------------------------------------------ #
class Observer(ABC):
    """Abstract base class for observers that respond to metrics updates."""

    @abstractmethod
    def update(self, metrics: Metrics) -> None:
        """Updates observer with the latest metrics.

        Args:
            metrics (Metrics): The metrics object containing the latest data.
        """
        pass
