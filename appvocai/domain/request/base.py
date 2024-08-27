#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/request/base.py                                                    #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday August 26th 2024 10:23:34 pm                                                 #
# Modified   : Tuesday August 27th 2024 03:05:11 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from appvocai.core.data import DataClass
from appvocai.infra.base.config import Config


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Request(DataClass):
    """Abstract base class for batch HTTP requests"""
    id: str = ""  # System generated UUID (default: "")
    date_time: datetime = None # Datetime the request was sent.
    index: int = 0  # The index or offset requested (default: 0)
    method: str = 'GET'  # The HTTP method used (GET, POST, etc.) (default: 'GET')


    def __post_init__(self) -> None:
        self.id = str(uuid4())

    @property
    def proxy(self) -> str:
        return Config().proxy

    @property
    @abstractmethod
    def baseurl(self) -> str:
        """Base URL for requests"""

    @property
    @abstractmethod
    def params(self) -> str:
        """HTTP REquest Parameters"""


# ------------------------------------------------------------------------------------------------ #
@dataclass
class RequestAsync(DataClass):
    """Encapsulates a list of requests"""


# ------------------------------------------------------------------------------------------------ #
class RequestGen(ABC):

    @abstractmethod
    def __iter__(self) -> RequestGen:
        """Initalizes the generation of Requests"""

    @abstractmethod
    def __next__(self) -> RequestAsync:
        """Generates the next request"""
