#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/base/request.py                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 03:50:26 am                                                   #
# Modified   : Sunday July 28th 2024 11:58:24 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Request Module"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from appstorestream.core.data import DataClass

# ------------------------------------------------------------------------------------------------ #


@dataclass
class AsyncRequest(DataClass):
    """Abstract base class for batch HTTP requests"""

# ------------------------------------------------------------------------------------------------ #
class AsyncRequestGen(ABC):

    @abstractmethod
    def __iter__(self):
        """Initalizes the generation of Requests"""

    @abstractmethod
    def __next__(self):
        """Generates the next request"""