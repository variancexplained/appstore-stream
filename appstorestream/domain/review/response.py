#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/domain/review/response.py                                           #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 05:53:12 am                                                   #
# Modified   : Thursday August 15th 2024 08:51:24 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Response Module"""
import logging
from dataclasses import dataclass
from datetime import datetime

from pytz import timezone

from appstorestream.domain.base.response import AsyncResponse

# ------------------------------------------------------------------------------------------------ #
tz = timezone("EST")
# ------------------------------------------------------------------------------------------------ #


class ReviewAsyncResponse(AsyncResponse):

    # TODO: Parse review results
    def parse_results(self, results: list) -> None:
        """Parse the results into a list of dictionaries."""
