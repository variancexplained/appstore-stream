#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /acquire/application/orchestration/task.py                                          #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday September 6th 2024 04:34:13 pm                                               #
# Modified   : Monday September 9th 2024 04:57:55 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Task Module"""
from acquire import TaskPassport
from acquire.core.enum import Status
from acquire.domain.artifact.request.base import AsyncRequest


# ------------------------------------------------------------------------------------------------ #
class Task:
    def __init__(self, async_request: AsyncRequest):
        self.passport = TaskPassport(owner=self, job_passport=job_passport)
        self._async_request = async_request
        self.status = Status.CREATED

    def execute(self) -> None:
        # Run the pipeline from Extract to Load
        self.status = Status.IN_PROGRESS
        self.run_stages()
        self.status = Status.COMPLETED

    def run_stages(self) -> None:
        extract_result = ExtractStage().run(artifact=self._async_request)
        transform_result = TransformStage().run(artifact=extract_result)
        LoadStage().run(transform_result)
