#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/job/job.py                                                    #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 02:14:31 pm                                              #
# Modified   : Wednesday August 28th 2024 06:47:02 pm                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Job Module"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, TypeVar
from uuid import uuid4

from appvocai.application.job.project import Project
from appvocai.application.task.base import Task
from appvocai.core.data import DataClass
from appvocai.core.date_time import format_duration, to_utc
from appvocai.core.enum import JobStatus

# ------------------------------------------------------------------------------------------------ #
T = TypeVar('T', bound="Task")
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
@dataclass
class Job(DataClass):
    """
    Represents a scraping job, encapsulating all related information and task management.

    Attributes:
        project (Project): The Project being scraped.
        id (str): Unique identifier for the job; auto-generated if not provided.
        description (str): Description of the job.
        _created (Optional[datetime]): Date and time the job was created.
        _scheduled (Optional[datetime]): Date and time the job is scheduled to start.
        _started (Optional[datetime]): Date and time the job was started.
        _updated (Optional[datetime]): Date and time the job was last updated.
        _completed (Optional[datetime]): Date and time the job was completed.
        _execution_time (float): The amount of time the job has run in seconds.
        last_page (int): The last page processed during scraping.
        status (JobStatus): Current status of the job from the JobStatus enum.
        cancellation_reason (Optional[str]): Reason for cancellation if applicable.
        success_rate (float): Percentage of successful scraping jobs.
        retry_count (int): Count of how many times the job has been retried.
        max_retries (int): Maximum number of retries allowed.
        _tasks (List[Task]): List of the job's Task objects.
        _task_idx (int): Index for tracking the current task being executed.
    """

    project: Project                          # Project object.
    id: str = ""                              # Unique identifier for the job; auto-generated if not provided.
    description: str = ""                     # Job description.
    _created: Optional[datetime] = None       # Date and time the job was created.
    _scheduled: Optional[datetime] = None     # Date and time the job is scheduled to start.
    _started: Optional[datetime] = None       # Date and time the job was started.
    _updated: Optional[datetime] = None       # Date and time the job was last updated.
    _completed: Optional[datetime] = None     # Date and time the job was completed.
    _execution_time: float = 0                # The amount of time the job has run in seconds.
    last_page: int = 0                        # The last page processed during scraping.
    status: JobStatus = JobStatus.CREATED      # Current status of the job from the JobStatus enum.
    cancellation_reason: Optional[str] = None  # Reason for cancellation if applicable.
    success_rate: float = 0.0                  # Percentage of successful scraping jobs.
    retry_count: int = 0                       # Count of how many times the job has been retried.
    max_retries: int = 3                       # Maximum number of retries allowed.
    _tasks: List[Task] = field(default_factory=list)  # List of the job's Task objects.
    _task_idx: int = 0                         # Index for tracking the current task being executed.

    def __post_init__(self) -> None:
        """
        Initializes the Job instance, setting the creation time, updated time,
        and generating a unique ID if not provided.
        """
        if not self.id:
            self.id = str(uuid4())  # Generate a UUID for the job ID
        self._created = datetime.now(timezone.utc)  # Set the creation time to the current UTC time
        self._updated = self._created                    # Set the updated time to the creation time
        self._task_idx = 0                              # Initialize task index to zero
        self.project.job_count += 1                     # Increment number of jobs for project
        if not self.description:
            self.description = f"Job Id: {self.id} to obtain {self.project.content_type} for the {self.project.category.value}"

    def __iter__(self) -> 'Job':
        """Return the Job instance itself for iteration."""
        return self

    def __next__(self) -> Task:
        """
        Retrieve the next task in the job's task list.

        Raises:
            StopIteration: If all tasks have been processed.

        Returns:
            Task: The next Task object in the job's task list.
        """
        if self._task_idx < len(self._tasks):
            task = self._tasks[self._task_idx]  # Get the current task
            self._task_idx += 1                  # Increment the task index for the next call
            return task
        else:
            msg = "The job is complete. No further tasks."
            logger.info(msg)                    # Log a message when there are no more tasks
            raise StopIteration()                 # Raise StopIteration to signal end of iteration

    @property
    def created(self) -> datetime:
        """Get the creation time of the job."""
        return self._created

    @property
    def scheduled(self) -> Optional[datetime]:
        """Get the scheduled time of the job."""
        return self._scheduled

    @property
    def started(self) -> Optional[datetime]:
        """Get the start time of the job."""
        return self._started

    @property
    def updated(self) ->  Optional[datetime]:
        """Get the last updated time of the job."""
        return self._updated

    @property
    def completed(self) -> Optional[datetime]:
        """Get the completion time of the job."""
        return self._completed

    @property
    def execution_time(self) -> float:
        """Get the total execution time of the job in seconds."""
        return self._execution_time

    def schedule(self, scheduled: datetime) -> None:
        """
        Schedule the job at a specified time, converting to UTC if needed.

        Args:
            scheduled (datetime): The date and time to schedule the job.
        """
        self.status = JobStatus.SCHEDULED                      # Update job status to SCHEDULED
        self._scheduled = to_utc(dt=scheduled)                 # Convert scheduled time to UTC
        self._updated = datetime.now(timezone.utc)             # Update the last updated time
        logger.info(f"{self.description} has been scheduled for {self._scheduled}.")

    def start(self) -> None:
        """Start the job and update its status and last updated time."""
        self.status = JobStatus.RUNNING                         # Update job status to RUNNING
        self._started = datetime.now(timezone.utc)             # Update the start time
        self._updated = self._started                          # Update the last updated time
        logger.info(f"Started {self.description} at {self._started}.")

    def update(self, last_page: int) -> None:
        """
        Update the job with the last page processed.

        Args:
            last_page (int): The last page number processed.
        """
        self._check_started()
        self.status = JobStatus.RUNNING                         # Keep status as RUNNING
        self.last_page = last_page                               # Set the last page processed
        self._updated = datetime.now(timezone.utc)             # Update the last updated time

    def cancel(self, reason: Optional[str] = None) -> None:
        """Cancel the job and update its status, optionally specifying a cancellation reason."""
        self.status = JobStatus.CANCELED                        # Update job status to CANCELED
        self._updated = datetime.now(timezone.utc)             # Update the last updated time
        self.cancellation_reason = reason
        logger.info(f"{self.description} canceled at {self._updated}.")
        if reason:
            logger.info(f"Cancellation reason: {reason}")

    def fail(self) -> None:
        """Mark the job as failed, update its status, and reset the task index."""
        self._check_started()
        self.status = JobStatus.FAILED                          # Update job status to FAILED
        self._updated = datetime.now(timezone.utc)             # Update the last updated time
        self._task_idx = 0                                      # Reset the task index for a new attempt
        logger.info(f"{self.description} failed at {self._updated}.")

    def complete(self) -> None:
        """
        Mark the job as completed, update its status, completion time, and execution time.
        """
        self._check_started()
        self._completed = datetime.now(timezone.utc)            # Set the completion time
        self.status = JobStatus.COMPLETED                       # Update job status to COMPLETED
        self._updated = self._completed                         # Update the last updated time
        self._task_idx = 0                                      # Reset the task index for a new attempt
        self._execution_time = (self._completed - self._started).total_seconds()

        logger.info(f"Completed {self.description}\nCompletion time: {self._completed}\nExecution time: {format_duration(self.execution_time)}")

    def retry(self) -> None:
        """Retry the job and reset the task index, incrementing the retry count."""
        if self.retry_count >= self.max_retries:
            raise RuntimeError(f"The number of retries has exceeded max retries.")
        self.retry_count += 1                                   # Increment the retry count
        self._task_idx = 0                                      # Reset the task index for a new attempt
        logger.info(f"Retry #{self.retry_count} for {self.description}")
        self.start()

    def add_task(self, task: T) -> None:
        """
        Add a new task to the job's task list.

        Args:
            task (Task): The task to be added to the job.

        Raises:
            TypeError: If the provided task is not of type Task.
        """
        if isinstance(task, Task):
            self._tasks.append(task)
            logger.info(f"Added task: {task} to {self.description}.")
        else:
            raise TypeError("Only Task instances can be added.")

    def _check_started(self) -> None:
        """Ensure the job has been started before performing certain actions."""
        if self.status not in {JobStatus.RUNNING, JobStatus.SCHEDULED}:
            raise RuntimeError("The job must be started before this action can be performed.")
