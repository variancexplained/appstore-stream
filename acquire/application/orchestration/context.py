#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /acquire/application/orchestration/context.py                                       #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 02:14:31 pm                                              #
# Modified   : Monday September 9th 2024 04:57:55 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Job Module"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from acquire.application.orchestration.project import Project
from acquire.core.data import DataClass
from acquire.core.enum import Category, DataType, Status
from acquire.infra.identity.idxgen import IDXGen
from acquire.toolkit.date import ThirdDateFormatter

# ------------------------------------------------------------------------------------------------ #
idxgen = IDXGen()
date4mtr = ThirdDateFormatter()
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class JobContext(DataClass):
    """
    Represents the context of a job, holding metadata, progress, and state information
    throughout the job's lifecycle.

    Attributes:
    -----------
    job_id : str
        Unique identifier for the job.
    category : Category
        The category the job belongs to (e.g., AppData or Reviews).
    data_type : DataType
        The type of data this job handles.
    description : str
        A description of the job.
    dt_created : datetime
        The date and time when the job was created.
    dt_scheduled : Optional[datetime]
        The scheduled start time of the job, if applicable.
    dt_started : Optional[datetime]
        The actual start time of the job.
    dt_updated : Optional[datetime]
        The time when the job was last updated.
    dt_ended : Optional[datetime]
        The time when the job ended.
    dt_completed : Optional[datetime]
        The time when the job was fully completed.
    start_page : int
        The initial page for scraping.
    last_page : int
        The last page processed during scraping.
    status : Status
        The current status of the job, as defined in the Status enum.

    Methods:
    --------
    create(cls, project: Project) -> JobContext:
        Creates a new JobContext instance based on the given project.

    execution_time(self) -> float:
        Calculates the total execution time of the job in seconds.

    start(self) -> None:
        Starts the job, updating the status and start time. Raises an error if the job is not in 'Created' status.

    update_progress(self, page: int) -> None:
        Updates the job's progress by recording the last page processed. Raises an error if the job is not 'In Progress'.

    end(self) -> None:
        Ends the job, marking it as 'Ended' and updating the time. Raises an error if the job is not 'In Progress'.

    complete(self) -> None:
        Completes the job, updating its status and completion time. Raises an error if the job is not 'Ended' or 'In Progress'.
    """

    job_id: str
    category: Category
    data_type: DataType
    description: str
    dt_created: datetime
    dt_scheduled: Optional[datetime] = None
    dt_started: Optional[datetime] = None
    dt_updated: Optional[datetime] = None
    dt_ended: Optional[datetime] = None
    dt_completed: Optional[datetime] = None
    start_page: int = 0
    last_page: int = 0
    status: Status = Status.CREATED

    @classmethod
    def create(cls, project: Project) -> JobContext:
        """
        Creates a new JobContext object based on a given project.

        Parameters:
        -----------
        project : Project
            The project that the job is associated with, containing category and data type details.

        Returns:
        --------
        JobContext
            A new JobContext instance with the initial metadata set.
        """
        now = datetime.now()
        return cls(
            job_id=idxgen.get_next_id(cls),
            category=project.category,
            data_type=project.data_type,
            description=f"{project.data_type.value} for the {project.category.display} category {date4mtr.to_HTTP_format(dt=now)}",
            dt_created=now,
            start_page=project.last_page_processed,
            last_page=project.last_page_processed,
        )

    @property
    def execution_time(self) -> float:
        """
        Calculates the total execution time of the job.

        Returns:
        --------
        float
            The execution time in seconds. If the job hasn't ended, returns the time from start to last update.
        """
        if self.dt_started:
            if self.dt_ended:
                return (self.dt_ended - self.dt_started).total_seconds()
            elif self.dt_updated:
                return (self.dt_updated - self.dt_started).total_seconds()
        return 0.0

    def start(self) -> None:
        """
        Starts the job and updates its status and start time.

        Raises:
        -------
        RuntimeError
            If the job's status is not 'Created'.
        """
        if self.status == Status.CREATED:
            self.status = Status.IN_PROGRESS
            self.dt_started = datetime.now()
        else:
            msg = f"Job start expects 'Created' state. Encountered {self.status.value}"
            logger.exception(msg)
            raise RuntimeError(msg)

    def update_progress(self, page: int) -> None:
        """
        Updates the job with the last page processed and records the update time.

        Parameters:
        -----------
        page : int
            The last page processed.

        Raises:
        -------
        RuntimeError
            If the job's status is not 'In Progress'.
        """
        if self.status == Status.IN_PROGRESS:
            self.last_page = page
            self.dt_updated = datetime.now()
        else:
            msg = f"Job update progress is valid for jobs in progress. Encountered job status of {self.status.value}."
            logger.exception(msg)
            raise RuntimeError(msg)

    def end(self) -> None:
        """
        Ends the job by marking it as 'Ended' and updating the end time.

        Raises:
        -------
        RuntimeError
            If the job's status is not 'In Progress'.
        """
        if self.status == Status.IN_PROGRESS:
            now = datetime.now()
            self.status = Status.ENDED
            self.dt_updated = now
            self.dt_ended = now
        else:
            msg = f"Job end is valid for jobs in progress. Encountered job status of {self.status.value}."
            logger.exception(msg)
            raise RuntimeError(msg)

    def complete(self) -> None:
        """
        Marks the job as completed, updating its status and recording the completion time.

        Raises:
        -------
        RuntimeError
            If the job's status is not 'Ended'.
        """
        if self.status == self.status == Status.ENDED:
            now = datetime.now()
            self.dt_updated = now
            self.dt_completed = now
            self.status = Status.COMPLETED
        else:
            msg = f"Job complete expects status of 'Ended'. Encountered {self.status.value}"
            logger.exception(msg)
            raise RuntimeError(msg)
