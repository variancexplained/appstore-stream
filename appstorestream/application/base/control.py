#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/base/control.py                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday July 29th 2024 12:58:10 am                                                   #
# Modified   : Monday July 29th 2024 02:03:02 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Control Module"""
from abc import ABC, abstractmethod

from dependency_injector.wiring import Provide, inject

from appstorestream.application.base.job import Job
from appstorestream.application.base.project import Project
from appstorestream.container import AppStoreStreamContainer
from appstorestream.core.enum import ProjectStatus
from appstorestream.infra.repo.uow import UoW


# ------------------------------------------------------------------------------------------------ #
class Controller(ABC):
    @inject
    def __init__(
        self,
        project_id: int,
        uow: UoW = Provide[AppStoreStreamContainer.data.uow],
    ) -> None:
        self._project_id = project_id
        self._uow = uow

    def get_project(self, project_id: int) -> Project:
        return self._uow.project_repo.get(id=project_id)

    @abstractmethod
    def get_job(self, project: Project) -> Job:
        """Returns a configured job."""

    def run(self) -> None:
        # Obtain the project from the repository
        project = self.get_project(project_id=self._project_id)
        # Create a job object for the Project and run it
        job = self.get_job(project=project)
        job.run()
        # Add the job to the repository
        job = self._uow.job_repo.add(job=job)
        # Update the project with job progress
        project = self._update_project(project=project, job=job)
        # Commit the project to the repository
        self._uow.project_repo.update(project=project)

    def _update_project(self, project: Project, job: Job) -> Project:
        project.bookmark = job.bookmark + 1
        project.n_jobs += 1
        project.last_job_id = job.job_id
        project.last_job_ended = job.ended
        project.last_job_status = job.status
        project.project_status = ProjectStatus.INACTIVE
        return project
