#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/base/builder.py                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 02:15:42 am                                                   #
# Modified   : Friday July 26th 2024 05:21:44 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from appstorestream.application.base.job import Job


# ------------------------------------------------------------------------------------------------ #
#                                       JOB BUILDER                                                #
# ------------------------------------------------------------------------------------------------ #
class JobBuilder(ABC):

    def __init__(self) -> None:
        super().__init__()
        self._name = None
        self._category_id = None
        self._scheduled = None
        self._job = None

    def by_name(self, name: str) -> JobBuilder:
        self._name = name
        return self

    def for_category_id(self, category_id: int) -> JobBuilder:
        self._category_id = category_id
        return self

    def at(self, scheduled: datetime) -> JobBuilder:
        self._scheduled = scheduled

    @abstractmethod
    def build(self) -> Job:
        """Constructs a Job Object"""

