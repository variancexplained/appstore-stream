#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/orchestration/task.py                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday September 6th 2024 04:34:13 pm                                               #
# Modified   : Friday September 6th 2024 05:27:01 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Task Module"""
from appvocai import JobPassport, TaskPassport
from appvocai.core.enum import Status
from appvocai.domain.artifact.request.base import AsyncRequest


# ------------------------------------------------------------------------------------------------ #
class Task:
    def __init__(self, job_passport: JobPassport, async_request: AsyncRequest):
        self.passport = TaskPassport(owner=self, job_passport=job_passport)
        self._async_request = async_request
        self.status = Status.CREATED

    def execute(self) -> None:
        # Run the pipeline from Extract to Load
        self.status = Status.IN_PROGRESS
        self.run_operations()
        self.status = Status.COMPLETED

    def run_operations(self) -> None:
        extract_result = ExtractOperation().run(artifact=self._async_request)
        transform_result = TransformOperation().run(artifact=extract_result)
        LoadOperation().run(transform_result)
