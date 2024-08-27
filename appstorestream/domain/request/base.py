#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/domain/request/base.py                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday August 26th 2024 10:23:34 pm                                                 #
# Modified   : Tuesday August 27th 2024 02:18:02 am                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

from appstorestream.core.data import DataClass
from appstorestream.infra.base.config import Config


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Request(DataClass):
    """Abstract base class for batch HTTP requests"""

    @property
    def proxy(self) -> str:
        return Config().proxy

    @property
    @abstractmethod
    def baseurl(self) -> str:
        """Base URL for requests"""


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
