#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_app_layer/test_job_package/test_job.py                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 28th 2024 09:19:25 pm                                              #
# Modified   : Thursday August 29th 2024 01:08:50 am                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import inspect
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd
import pytest

from appvocai.application.job.job import Job
from appvocai.application.job.project import Project
from appvocai.application.task.base import Task
from appvocai.core.enum import *

# ------------------------------------------------------------------------------------------------ #
# pylint: disable=missing-class-docstring, line-too-long
# mypy: ignore-errors
# ------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"


@pytest.mark.job
class TestJob:  # pragma: no cover
    # ============================================================================================ #
    def test_job_lifecycle(self, project, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        # Validate project
        assert project.category == Category.EDUCATION # From comftest
        assert project.content_type == ContentType.APPREVIEW
        assert project.frequency == ProjectFrequency.WEEKLY
        assert project.status == ProjectStatus.IDLE

        # Create job object
        job = Job(project=project)

        # Test inatantiation
        assert job.id
        assert isinstance(job.project, Project)
        assert 'AppReview' in job.description
        assert job.created
        assert isinstance(job.created, datetime)
        assert job.status == JobStatus.CREATED
        logger.info(job)

        # Schedule job
        scheduled = datetime.now(timezone.utc) + timedelta(days=1)
        job.schedule(scheduled=scheduled)
        last_updated = job.updated
        assert job.scheduled == scheduled
        assert job.updated
        assert job.status == JobStatus.SCHEDULED
        logger.info(job)

        # Start job
        job.start()
        assert job.started
        assert job.status == JobStatus.RUNNING
        assert job.updated
        assert job.updated > last_updated
        assert project.job_count == 1
        assert project.status == ProjectStatus.ACTIVE
        last_updated = job.updated
        logger.info(job)
        logger.info(project)

        time.sleep(0.25)

        # Update progress
        job.update_progress(page=20)
        assert job.last_page == 20
        assert job.updated > last_updated
        assert project.max_page_processed == 20
        assert project.last_page_processed == 20
        last_updated = job.updated
        logger.info(job)
        logger.info(project)

        time.sleep(0.25)

        # Update progress again...
        job.update_progress(page=40)
        assert job.last_page == 40
        assert job.updated > last_updated
        assert project.max_page_processed == 40
        assert project.last_page_processed == 40
        last_updated = job.updated
        logger.info(job)
        logger.info(project)

        # Complete the job
        job.complete()
        assert job.status == JobStatus.COMPLETED
        assert job.updated > last_updated
        assert isinstance(job.completed,datetime)
        assert job.execution_time > 0
        assert project.job_successes == 1
        assert project.success_rate == 100.0
        assert project.status == ProjectStatus.IDLE
        logger.info(job)
        logger.info(project)


        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
    # ============================================================================================ #
    def test_second_job_starts_from_page_0(self, project, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        job = Job(project=project)

        # Start Job
        job.start()
        assert job.started
        assert job.status == JobStatus.RUNNING
        assert job.updated
        assert project.job_count == 2
        assert project.status == ProjectStatus.ACTIVE
        last_updated = job.updated
        logger.info(job)
        logger.info(project)

        # Update progress
        job.update_progress(page=10)
        assert job.last_page == 10
        assert job.updated > last_updated
        assert project.max_page_processed == 40
        assert project.last_page_processed == 10
        last_updated = job.updated
        logger.info(job)
        logger.info(project)

        # Complete the job
        job.complete()
        assert job.status == JobStatus.COMPLETED
        assert job.updated > last_updated
        assert isinstance(job.completed,datetime)
        assert project.job_successes == 2
        assert project.success_rate == 100.0
        assert project.status == ProjectStatus.IDLE
        logger.info(job)
        logger.info(project)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_schedule_validation(self, project, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        job = Job(project=project)

        scheduled = datetime.now(timezone.utc) + timedelta(days=-1)
        with pytest.raises(ValueError):
            job.schedule(scheduled=scheduled)

        scheduled = datetime.now(timezone.utc) + timedelta(days=1)
        job.cancel()
        with pytest.raises(RuntimeError):
            job.schedule(scheduled=scheduled)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_start_validation(self, project, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        job = Job(project=project)
        job.cancel()

        with pytest.raises(RuntimeError):
            job.start()
        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_update_validation(self, project, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        job = Job(project=project)
        with pytest.raises(RuntimeError):
            job.update_progress(page=10)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_cancellation(self, project, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        job = Job(project=project)
        job.cancel()
        assert job.status == JobStatus.CANCELED
        assert job.cancellation_reason is None

        job.cancel(reason="test_reason")
        assert job.cancellation_reason == "test_reason"
        with pytest.raises(RuntimeError):
            job.update_progress(page=10)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_fail(self, project, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        job = Job(project=project)
        job.start()
        job.fail()
        assert job.status == JobStatus.FAILED
        assert project.job_count == 3
        assert round(project.success_rate,1) == 66.7

        # Check validation
        with pytest.raises(RuntimeError):
            job.fail()

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_retry(self, project, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        job = Job(project=project)

        # Start job
        job.start()
        assert project.job_count == 4

        # Test retry
        for i in range(3):
            job.fail()
            assert job.status == JobStatus.FAILED
            job.retry()
            assert job.status == JobStatus.RUNNING

        job.fail()
        with pytest.raises(RuntimeError):
            job.retry()
        assert job.status == JobStatus.FAILED
        assert project.job_count == 4
        assert project.success_rate == 50.0

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_task_handling(self, project, mock_task, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        job = Job(project=project)

        # Start job
        for i in range(3):
            job.add_task(mock_task)

        n_tasks = 0
        for task in job:
            assert isinstance(task, Task)
            n_tasks += 1

        assert n_tasks == 3

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)