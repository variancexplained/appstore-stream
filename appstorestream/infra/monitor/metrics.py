#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/monitor/metrics.py                                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday August 20th 2024 03:47:24 am                                                #
# Modified   : Wednesday August 21st 2024 07:58:15 am                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from abc import ABC
from dataclasses import dataclass

from appstorestream.core.data import DataClass


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Metrics(DataClass):
    """Abstract Base Class for Metrics"""


# ------------------------------------------------------------------------------------------------ #
class MetricsRegistry:
    # TODO: Integrate Metrics Registration with Kubernetes and Docker
    def update(self, name: str, value: float) -> None:
        """Adds Metric to"""
