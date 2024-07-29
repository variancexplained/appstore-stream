#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/base/project.py                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Sunday July 28th 2024 12:54:32 pm                                                   #
# Modified   : Sunday July 28th 2024 01:50:44 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Project Base Module"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from appstorestream.core.data import DataClass
from appstorestream.core.enum import Dataset, ProjectStatus


@dataclass
class Project(DataClass):
    project_id: int
    dataset: Dataset
    category_id: int
    category: str
    project_priority: int = 3
    progress: int = 0
    n_jobs: int = 0
    last_job_id: Optional[str] = None
    dt_last_job: Optional[datetime] = None
    project_status: ProjectStatus = ProjectStatus.NOT_STARTED