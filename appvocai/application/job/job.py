#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/job/job.py                                                    #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 02:14:31 pm                                              #
# Modified   : Monday September 2nd 2024 12:31:52 am                                               #
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
from appvocai.core.enum import JobStatus
from appvocai.toolkit.date import format_duration, to_utc

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
    created: Optional[datetime] = None       # Date and time the job was created.
    scheduled: Optional[datetime] = None     # Date and time the job is scheduled to start.
    started: Optional[datetime] = None       # Date and time the job was started.
    updated: Optional[datetime] = None       # Date and time the job was last updated.
    completed: Optional[datetime] = None     # Date and time the job was completed.
    _execution_time: float = 0                # The amount of time the job has run in seconds.
    start_page: int = 0                       # The start page for scaping.
    last_page: int = 0                        # The last page processed during scraping.
    status: JobStatus = JobStatus.CREATED      # Current status of the job from the JobStatus enum.
    cancellation_reason: Optional[str] = None  # Reason for cancellation if applicable.
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
        self.created = datetime.now(timezone.utc)
        if not self.description:
            self.description = f"Job to obtain {self.project.content_type.value} for the {self.project.category.display_name} category." # type: ignore

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
    def execution_time(self) -> float:
        """Get the total execution time of the job in seconds."""
        return self._execution_time

    def schedule(self, scheduled: datetime) -> None:
        """
        Schedule the job at a specified time, converting to UTC if needed.

        Args:
            scheduled (datetime): The date and time to schedule the job.

        Raises:
            ValueError: If the scheduled time is in the past or if the job cannot be scheduled in its current state.
        """
        if scheduled < datetime.now(timezone.utc):
            logger.error("Scheduled time cannot be in the past.")
            raise ValueError("Scheduled time cannot be in the past.")
        if self.status not in {JobStatus.CREATED, JobStatus.SCHEDULED}:
            logger.error(f"Cannot schedule job {self.id} from status {self.status.value}.")
            raise RuntimeError(f"Cannot schedule job {self.id} from status {self.status.value}.")
        self.status = JobStatus.SCHEDULED
        self.scheduled = to_utc(dt=scheduled)
        self.updated = datetime.now(timezone.utc)
        logger.info(f"{self.description} has been scheduled for {self.scheduled}.")



    def start(self) -> None:
        """Start the job and update its status and last updated time."""
        if self.status not in {JobStatus.CREATED, JobStatus.SCHEDULED}:
            msg = f"Cannot start job {self.id} from status {self.status.value}."
            logger.error(msg)
            raise RuntimeError(msg)

        self.status = JobStatus.RUNNING
        self.started = datetime.now(timezone.utc)
        self.updated = self.started
        self.project.job_started()
        logger.info(f"Started {self.description} at {self.started}.")

    def update_progress(self, page: int) -> None:
        """
        Update the job with the last page processed.

        Args:
            last_page (int): The last page number processed.

        Raises:
            RuntimeError: If the job is not running.
        """
        self._check_running()  # Confirm job is in running state
        self.last_page = page
        self.project.update_progress(page=page)
        self.updated = datetime.now(timezone.utc)

    def cancel(self, reason: Optional[str] = None) -> None:
        """
        Cancel the job and update its status, optionally specifying a cancellation reason.

        Args:
            reason (Optional[str]): Reason for cancellation if applicable.
        """
        self.status = JobStatus.CANCELED  # Update job status to CANCELED
        self.updated = datetime.now(timezone.utc)
        self.cancellation_reason = reason
        logger.info(f"{self.description} canceled at {self.updated}.")
        if reason:
            logger.info(f"Cancellation reason: {reason}")


    def fail(self) -> None:
        """Mark the job as failed, update its status, and reset the task index."""
        self._check_running()
        self.status = JobStatus.FAILED                          # Update job status to FAILED
        self.updated = datetime.now(timezone.utc)               # Update the last updated time
        self._task_idx = 0                                      # Reset the task index for a new attempt
        logger.info(f"{self.description} failed at {self.updated}.")

    def complete(self) -> None:
        """
        Mark the job as completed, update its status, completion time, and execution time.

        Raises:
            RuntimeError: If the job is not running.
        """
        self._check_running()
        self.completed = datetime.now(timezone.utc)
        self.status = JobStatus.COMPLETED
        self.updated = self.completed
        self.project.job_completed()

        # Compute execution time
        if self.started:
            self._execution_time = (self.completed - self.started).total_seconds()
        logger.info(f"Completed {self.description}\nCompletion time: {self.completed}\nExecution time: {self._execution_time:.2f} seconds.")

    def retry(self) -> None:
        """Retry the job and reset the task index, incrementing the retry count."""
        self._check_retry()
        if self.retry_count < self.max_retries:
            self.retry_count += 1                                   # Increment the retry count
            self._task_idx = 0                                      # Reset the task index for a new attempt
            self.status = JobStatus.RUNNING                         # Reset in case status is failed.
            self.started = datetime.now(timezone.utc)              # Reset start time
            self.updated = self.started
            logger.info(f"Retry #{self.retry_count} for {self.description}")
        else:
            msg = f"Maximum retries exceed for job id: {self.id}"
            logger.exception(msg)
            raise RuntimeError(msg)


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
            self.updated = datetime.now(timezone.utc)
            logger.info(f"Added task: {task} to {self.description}.")
        else:
            msg = f"Expected a Task object but received an object of type {type(task)}."
            logger.exception(msg)
            raise TypeError(msg)

    def _check_running(self) -> None:
        """Ensure the job is running before performing certain actions."""
        if self.status != JobStatus.RUNNING:
            raise RuntimeError(f"The job must be running before this action can be performed. Current status is {self.status.value}")

    def _check_retry(self) -> None:
        """Ensure the job is running before performing certain actions."""
        if self.status not in {JobStatus.FAILED, JobStatus.CANCELED}:
            raise RuntimeError(f"The job {self.id} must be failed or canceled before this action can be performed. Current status is {self.status.value}")

