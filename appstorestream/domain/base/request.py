#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/domain/base/request.py                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 03:50:26 am                                                   #
# Modified   : Monday July 29th 2024 02:06:01 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Request Module"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from appstorestream.core.data import DataClass
from appstorestream.domain.base.service import Service

# ------------------------------------------------------------------------------------------------ #


@dataclass
class AsyncRequest(DataClass):
    """Abstract base class for batch HTTP requests"""


# ------------------------------------------------------------------------------------------------ #
class AsyncRequestGen(Service):

    @abstractmethod
    def __iter__(self):
        """Initalizes the generation of Requests"""

    @abstractmethod
    def __next__(self):
        """Generates the next request"""
