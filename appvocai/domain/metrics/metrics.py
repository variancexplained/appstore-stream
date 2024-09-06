#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/metrics/metrics.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday September 6th 2024 07:20:22 am                                               #
# Modified   : Friday September 6th 2024 04:31:31 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Extract Metrics Module"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from appvocai.core.data import DataClass
from appvocai.core.enum import DataType, OperationType


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Metrics(DataClass):

    project_id: int
    job_id: int
    task_id: int
    data_type: DataType
    operation_type: OperationType
    instances: int = 0
    dt_started: Optional[datetime] = None
    dt_stopped: Optional[datetime] = None
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
    speedup: float = 0.0
    size: float = 0.0
