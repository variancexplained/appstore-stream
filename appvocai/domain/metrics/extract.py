#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/metrics/extract.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday September 6th 2024 07:20:22 am                                               #
# Modified   : Friday September 6th 2024 08:47:18 am                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Extract Metrics Module"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from appvocai.core.data import DataClass
from appvocai.core.enum import DataType, TaskType


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ExtractMetrics(DataClass):
    """
    A data class for capturing and storing metrics related to the Extract phase of a job/task.

    Attributes:
    ----------
    job_id : Optional[int]
        The identifier for the job this extract operation is associated with. Defaults to None.

    data_type : Optional[DataType]
        The type of data being extracted (e.g., AppData, Reviews). Defaults to None.

    task_id : Optional[int]
        The identifier for the specific task within the job. Defaults to None.

    task_type : TaskType
        The type of task being performed. Defaults to TaskType.EXTRACT.

    request_id : Optional[int]
        The identifier for the request being tracked. Defaults to None.

    starttime : Optional[datetime]
        The timestamp indicating when the extract operation started. Defaults to None.

    stoptime : Optional[datetime]
        The timestamp indicating when the extract operation stopped. Defaults to None.

    duration : float
        The total time taken for the extract operation, in seconds. Defaults to 0.0.

    requests : int
        The number of requests made during the extract operation. Defaults to 0.

    latency_min : float
        The minimum latency (in seconds) observed during the extract operation. Defaults to 0.0.

    latency_average : float
        The average latency (in seconds) observed during the extract operation. Defaults to 0.0.

    latency_median : float
        The median latency (in seconds) observed during the extract operation. Defaults to 0.0.

    latency_max : float
        The maximum latency (in seconds) observed during the extract operation. Defaults to 0.0.

    latency_std : float
        The standard deviation of latency (in seconds) observed during the extract operation. Defaults to 0.0.

    throughput_min : float
        The minimum throughput (requests per second) observed during the extract operation. Defaults to 0.0.

    throughput_average : float
        The average throughput (requests per second) observed during the extract operation. Defaults to 0.0.

    throughput_median : float
        The median throughput (requests per second) observed during the extract operation. Defaults to 0.0.

    throughput_max : float
        The maximum throughput (requests per second) observed during the extract operation. Defaults to 0.0.

    throughput_std : float
        The standard deviation of throughput (requests per second) observed during the extract operation. Defaults to 0.0.

    speedup : float
        The calculated speedup factor based on the job's concurrency and performance during extraction. Defaults to 0.0.

    size : float
        The total size of data (in bytes or another relevant unit) processed during the extract operation. Defaults to 0.0.

    Methods:
    -------
    as_dict() -> Dict[str, Union[str, int, float, datetime, None]]:
        Converts the ExtractMetrics object into a dictionary, where `data_type` and `task_type`
        are converted to their string values (if present). Inherited method from DataClass.
    """

    job_id: Optional[int] = None
    data_type: Optional[DataType] = None
    task_id: Optional[int] = None
    task_type: TaskType = TaskType.EXTRACT
    request_id: Optional[int] = None
    dt_started: Optional[datetime] = None
    dt_stopped: Optional[datetime] = None
    duration: float = 0.0
    requests: int = 0
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
