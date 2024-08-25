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
# Modified   : Sunday August 25th 2024 01:10:33 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Request Module"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from appstorestream.core.data import DataClass
from appstorestream.domain.base.service import DomainService

# ------------------------------------------------------------------------------------------------ #


@dataclass
class AsyncRequest(DataClass):
    """Abstract base class for batch HTTP requests"""


# ------------------------------------------------------------------------------------------------ #
class AsyncRequestGen(DomainService):

    @abstractmethod
    def __iter__(self) -> AsyncRequestGen:
        """Initalizes the generation of Requests"""

    @abstractmethod
    def __next__(self) -> AsyncRequest:
        """Generates the next request"""
