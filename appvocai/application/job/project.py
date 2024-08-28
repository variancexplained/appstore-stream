#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/job/project.py                                                #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 01:30:04 am                                              #
# Modified   : Wednesday August 28th 2024 06:48:15 pm                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4

from appvocai.core.data import DataClass
from appvocai.core.enum import (Category, ContentType, ProjectFrequency,
                                ProjectStatus)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Project(DataClass):
    """
    Represents a scraping project, encapsulating the related configuration and state.

    Attributes:
        category (Category): The category of the project, defined in the Category enum.
        content_type (ContentType): The type of data being scraped (e.g., "AppData", "AppReview"),
            defined in the ContentType enum.
        id (str): Unique identifier for the project; auto-generated if not provided during initialization.
        frequency (ProjectFrequency): The frequency of scraping jobs, defaulting to WEEKLY.
        last_job_executed (Optional[datetime]): UTC timestamp of the last executed job; None if never executed.
        next_scheduled_job (Optional[datetime]): Timestamp of the next scheduled job; None if not scheduled.
        job_count (int): Total number of jobs created for this project; starts at 0.
        success_rate (float): Percentage of successful jobs; starts at 0.0%.
        status (ProjectStatus): Current status of the project, defaulting to IDLE.
    """

    category: Category                          # Category of the project, defined in the Category enum.
    content_type: ContentType                   # Type of data being scraped, defined in ContentType enum.
    id: str = ""                                # Unique identifier for the project; initialized in __post_init__.
    frequency: ProjectFrequency = ProjectFrequency.WEEKLY  # Frequency of scraping jobs; defaults to WEEKLY.
    last_job_executed: Optional[datetime] = None  # UTC Timestamp of the last executed job; None if never executed.
    next_scheduled_job: Optional[datetime] = None  # Timestamp of the next scheduled job; None if not scheduled.
    job_count: int = 0                          # Total number of jobs created; starts at 0.
    success_rate: float = 0.0                   # Percentage of successful jobs; starts at 0.0%.
    status: ProjectStatus = ProjectStatus.IDLE   # Project status; defaults to IDLE.

    def __post_init__(self) -> None:
        """
        Initializes the Project instance, setting a unique ID if one is not provided.

        This method is called automatically after the object is created, ensuring that
        the project has a unique identifier for tracking purposes.
        """
        if not self.id:
            self.id = str(uuid4())  # Generate a UUID for the project ID



