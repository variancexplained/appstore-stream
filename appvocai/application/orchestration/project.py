#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/orchestration/project.py                                      #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 01:30:04 am                                              #
# Modified   : Friday September 6th 2024 07:16:13 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
# %%
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from appvocai.core.data import DataClass
from appvocai.core.enum import Category, DataType, ProjectFrequency, ProjectStatus
from appvocai.infra.identity.passport import ProjectPassport


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Project(DataClass):
    """
    Represents a scraping project, encapsulating the related configuration and state.

    Attributes:
        passport (Passport): The identity for the Project
        category (Category): The category of the project, defined in the Category enum.
        data_type (DataType): The type of data being scraped (e.g., "AppData", "AppReview"),
            defined in the DataType enum.
        frequency (ProjectFrequency): The frequency of scraping jobs, defaulting to WEEKLY.
        max_page_processed (int): The highest page processed for the project, used to track the progress of scraping.
        last_page_processed (int): Last page processed will be used as the starting page for resume jobs.
        last_job_executed (Optional[datetime]): UTC timestamp of the last executed job; None if never executed.
        next_scheduled_job (Optional[datetime]): Timestamp of the next scheduled job; None if not scheduled.
        job_count (int): Total number of jobs created for this project; starts at 0.
        job_successes (int): Number of successful jobs; starts at 0.
        success_rate (float): Percentage of successful jobs; computed dynamically based on job_count and job_successes.
        status (ProjectStatus): Current status of the project, defaulting to IDLE.
    """

    category: Category  # Category of the project, defined in the Category enum.
    data_type: DataType  # Type of data being scraped, defined in DataType enum.
    passport: Optional[ProjectPassport] = None
    frequency: ProjectFrequency = (
        ProjectFrequency.WEEKLY
    )  # Frequency of scraping jobs; defaults to WEEKLY.
    max_page_processed: int = (
        0  # The highest page processed for the project; starts at 0.
    )
    last_page_processed: int = (
        0  # Last page processed; will be the starting page for resume jobs.
    )
    last_job_executed: Optional[datetime] = (
        None  # UTC Timestamp of the last executed job; None if never executed.
    )
    next_scheduled_job: Optional[datetime] = (
        None  # Timestamp of the next scheduled job; None if not scheduled.
    )
    job_count: int = 0  # Total number of jobs created; starts at 0.
    job_successes: int = 0  # Number of successful jobs; starts at 0.
    status: ProjectStatus = ProjectStatus.IDLE  # Project status; defaults to IDLE.

    def __post_init__(self) -> None:
        """
        Initializes the Project instance, setting a unique ID if one is not provided.

        This method is called automatically after the object is created, ensuring that
        the project has a unique identifier for tracking purposes.
        """
        if not self.passport:
            self.passport = ProjectPassport(
                self, category=self.category, data_type=self.data_type
            )

    @property
    def success_rate(self) -> float:
        """
        Computes the success rate for the project.

        Returns:
            float: The success rate as a percentage. Returns 0.0 if no jobs have been created.
        """
        if self.job_count:
            return self.job_successes / self.job_count * 100
        else:
            return 0.0

    def job_started(self) -> None:
        """
        Increments the job count and updates the project status to ACTIVE.

        This method should be called when a new scraping job is initiated.
        """
        self.job_count += 1
        self.status = ProjectStatus.ACTIVE

    def update_progress(self, page: int) -> None:
        """
        Updates the last page processed and the maximum page processed for the project.

        This method should be called with the current page number after processing a page.
        It updates the last_page_processed to the current page and checks if the current
        page exceeds the max_page_processed, updating it if necessary.

        Args:
            page (int): The current page number being processed.
        """
        self.last_page_processed = page  # Update the last processed page
        if self.max_page_processed < page:
            self.max_page_processed = page  # Update max_page if current page is higher

    def job_completed(self) -> None:
        """
        Increments the count of successful jobs and updates the timestamp of the last executed job.

        This method should be called when a scraping job has been completed successfully.
        It also sets the last_job_executed to the current UTC time to reflect when the job completed.
        """
        self.job_successes += 1
        self.last_job_executed = (
            datetime.now()
        )  # Set the last executed time to now in UTC
        self.status = ProjectStatus.IDLE


# ------------------------------------------------------------------------------------------------ #
# Usage
project = Project(category=Category.BOOKS, data_type=DataType.APPREVIEW)
print(project.passport)
