#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/request.py                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 03:50:26 am                                                   #
# Modified   : Friday July 26th 2024 11:31:31 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Application Layer Base Module"""
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd

from appstorestream.application.base.service import Service, ServiceConfig
from appstorestream.core.data import DataClass

# ------------------------------------------------------------------------------------------------ #


@dataclass
class AsyncRequest(DataClass):
    """Abstract base class for asyncronous HTTP requests"""

# ------------------------------------------------------------------------------------------------ #
@dataclass
class AsyncRequestGenConfig(ServiceConfig):
    max_requests: int = sys.maxsize

# ------------------------------------------------------------------------------------------------ #
class AsyncRequestGen(Service):

    @abstractmethod
    def __iter__(self):
        """Initalizes the generation of Requests"""

    @abstractmethod
    def __next__(self):
        """Generates the next request"""