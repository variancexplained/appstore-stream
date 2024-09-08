#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/monitor/errors.py                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday September 6th 2024 10:48:51 pm                                               #
# Modified   : Friday September 6th 2024 10:51:38 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Error Metrics Module"""
from dataclasses import dataclass
from datetime import datetime

from appvocai.core.data import DataClass
from appvocai.core.enum import DataType, OperationType


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ErrorLog(DataClass):

    project_id: int
    job_id: int
    task_id: int
    data_type: DataType
    operation_type: OperationType
    error_type: str
    error_code: int
    error_description: str
    dt_error: datetime
