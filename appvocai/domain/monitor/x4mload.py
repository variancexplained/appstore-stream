#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/monitor/x4mload.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday September 6th 2024 07:20:22 am                                               #
# Modified   : Friday September 6th 2024 11:29:27 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Review Metrics Module"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from appvocai.core.data import DataClass
from appvocai.core.enum import DataType, OperationType


# ------------------------------------------------------------------------------------------------ #
@dataclass
class X4MLoadMetrics(DataClass):

    project_id: int
    job_id: int
    task_id: int
    data_type: DataType
    operation_type: OperationType
    instances: int = 0
    dt_started: Optional[datetime] = None
    dt_ended: Optional[datetime] = None
    duration: float = 0.0
    latency_min: float = 0.0
    latency_average: float = 0.0
    latency_median: float = 0.0
    latency_max: float = 0.0
    latency_std: float = 0.0
    throughput_min: float = 0.0
    throughput_average: float = 0.0
    throughput_median: float = 0.0
    throughput_max: float = 0.0
    throughput_std: float = 0.0
