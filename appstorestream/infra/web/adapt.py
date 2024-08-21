#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/web/adapt.py                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 04:44:47 am                                                   #
# Modified   : Wednesday August 21st 2024 08:46:46 am                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Autothrottle Module"""
from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Union

import numpy as np

from appstorestream.core.data import DataClass
from appstorestream.core.service import NestedNamespace
from appstorestream.infra.monitor.metrics import MetricsRegistry


# ------------------------------------------------------------------------------------------------ #
#                                        ADAPTER                                                   #
# ------------------------------------------------------------------------------------------------ #
class Adapter(ABC):

    @abstractmethod
    def adapt(self, session_metrics: SessionMetrics) -> Union[float, int]:
        """Computes the value to adap"""


# ------------------------------------------------------------------------------------------------ #
#                                     ADAPTER STATE                                                #
# ------------------------------------------------------------------------------------------------ #
class AdapterState(ABC):
    @abstractmethod
    def execute(self, adapter: Adapter) -> None:
        """Executes adapter methods for the current state."""

    @abstractmethod
    def transition(self, adapter: Adapter) -> None:
        """Sets state on the adapter if state is complete."""


# ------------------------------------------------------------------------------------------------ #
class Adapter(ABC):
    def __init__(self, initial_state: AdapterState):
        self._state = initial_state

    def set_state(self, new_state: AdapterState) -> None:
        self._state = new_state

    async def execute(self) -> None:
        await self._state.execute(self)

    def transition(self) -> None:
        self._state.transition(self)
