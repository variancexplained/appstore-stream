#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/appdata/extract/repo.py                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 09:14:08 am                                                   #
# Modified   : Friday July 26th 2024 04:49:10 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import json
from dataclasses import dataclass
from typing import TypeVar

from appstorestream.application.base.repo import AppLayerRepo
from appstorestream.application.base.service import ServiceConfig
from appstorestream.core.enum import DatabaseSet

# ------------------------------------------------------------------------------------------------ #
T = TypeVar('T')
# ------------------------------------------------------------------------------------------------ #
#                               APP DATA JOB REPO CONFIG                                           #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class AppDataJobRepoConfig(ServiceConfig):
    dbset: DatabaseSet = DatabaseSet.CONTROL



# ------------------------------------------------------------------------------------------------ #
#                                   APP DATA JOB REPO                                              #
# ------------------------------------------------------------------------------------------------ #
class AppDataJobRepo(AppLayerRepo[T]):
    """Repository for managing AppData jobs."""

    def add(self, job: T) -> None:
        job_data = json.dumps(job.__dict__)
        self.redis_client.set(f"appdata_job:{job.id}", job_data)

    def get(self, job_id: str) -> T:
        job_data = self.redis_client.get(f"appdata_job:{job_id}")
        if job_data is None:
            return None
        return json.loads(job_data)

    def update(self, job: T) -> None:
        job_data = json.dumps(job.__dict__)
        self.redis_client.set(f"appdata_job:{job.id}", job_data)

    def delete(self, job_id: str) -> None:
        self.redis_client.delete(f"appdata_job:{job_id}")
