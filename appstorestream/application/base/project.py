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
# Modified   : Monday July 29th 2024 01:59:08 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Project Base Module"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from appstorestream.application.base.job import Job, JobConfig, JobMeta, JobStatus
from appstorestream.core.data import DataClass
from appstorestream.core.enum import Dataset, ProjectStatus


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Project(DataClass):
    """
    Represents a project with associated metadata and state.

    This class encapsulates information about a project, including its unique identifier, dataset, category, priority,
    bookmark, job management, and status. It is designed to track the lifecycle and details of a project.

    Attributes:
        project_id (int): Unique identifier for the project.
        dataset (Dataset): The dataset associated with the project.
        category_id (int): Identifier for the category to which the project belongs.
        category (str): Name or description of the category.
        project_priority (int, optional): Priority level of the project. Default is 3.
        bookmark (int, optional): Current bookmark percentage of the project. Default is 0.
        n_jobs (int, optional): Number of jobs associated with the project. Default is 0.
        last_job_id (Optional[str], optional): Identifier of the last job associated with the project. Default is None.
        dt_last_job (Optional[datetime], optional): Date and time when the last job was completed. Default is None.
        project_status (ProjectStatus, optional): Current status of the project. Default is ProjectStatus.NOT_STARTED.
    """

    project_id: int
    dataset: Dataset
    category_id: int
    category: str
    project_priority: int = 3
    bookmark: int = 0
    n_jobs: int = 0
    last_job_id: Optional[str] = None
    last_job_ended: Optional[datetime] = None
    last_job_status: Optional[JobStatus] = None
    project_status: ProjectStatus = ProjectStatus.NOT_STARTED
