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
# Modified   : Tuesday August 27th 2024 12:37:52 am                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict

from appstorestream.core.data import DataClass


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Request(DataClass):
    """Abstract base class for batch HTTP requests"""

    @property
    @abstractmethod
    def baseurl(self) -> str:
        """Base URL for requests"""
