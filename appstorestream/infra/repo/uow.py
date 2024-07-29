#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/repo/uow.py                                                   #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Sunday July 28th 2024 08:58:35 pm                                                   #
# Modified   : Monday July 29th 2024 03:33:04 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import logging

from appstorestream.infra.database.base import Database
from appstorestream.infra.repo.appdata import AppDataRepo
from appstorestream.infra.repo.job import JobRepo
from appstorestream.infra.repo.project import ProjectRepo
from appstorestream.infra.repo.review import ReviewRepo


# ------------------------------------------------------------------------------------------------ #
#                                       UNIT OF WORK CLASS                                         #
# ------------------------------------------------------------------------------------------------ #
class UoW:
    """Unit of Work class encapsulating the repositories used in project objects and manages database transactions.

    This class provides a unified interface for interacting with multiple repositories and managing transactions.
    It handles the lifecycle of a database connection and ensures that operations across repositories are coordinated.
    """

    def __init__(
        self,
        database: Database,
        appdata_repo: AppDataRepo,
        review_repo: ReviewRepo,
        project_repo: ProjectRepo,
        job_repo: JobRepo,
    ) -> None:
        """
        Initializes the Unit of Work with the specified repositories and database connection.

        Args:
            database (Database): The database instance used for transaction management.
            appdata_repo (DomainLayerRepo): Repository for handling app data in the domain layer.
            review_repo (DomainLayerRepo): Repository for handling reviews in the domain layer.
            project_repo (AppLayerRepo): Repository for handling projects in the application layer.
            job_repo (AppLayerRepo): Repository for handling jobs in the application layer.
        """
        self._database = database
        self._appdata_repo = appdata_repo
        self._review_repo = review_repo
        self._project_repo = project_repo
        self._job_repo = job_repo

        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    @property
    def database(self) -> Database:
        """
        Returns the database instance used for transaction management.

        Returns:
            Database: The database instance.
        """
        return self._database

    @property
    def appdata_repo(self) -> AppDataRepo:
        """
        Returns the repository for handling app data, initialized with the database instance.

        Returns:
            DomainLayerRepo: The app data repository.
        """
        return self._appdata_repo(database=self._database)

    @property
    def review_repo(self) -> ReviewRepo:
        """
        Returns the repository for handling reviews, initialized with the database instance.

        Returns:
            DomainLayerRepo: The review repository.
        """
        return self._review_repo(database=self._database)

    @property
    def project_repo(self) -> ProjectRepo:
        """
        Returns the repository for handling projects, initialized with the database instance.

        Returns:
            AppLayerRepo: The project repository.
        """
        return self._project_repo(database=self._database)

    @property
    def job_repo(self) -> JobRepo:
        """
        Returns the repository for handling jobs, initialized with the database instance.

        Returns:
            AppLayerRepo: The job repository.
        """
        return self._job_repo(database=self._database)

    def connect(self) -> None:
        """
        Establishes a connection to the database.

        This method must be called before performing any database operations.
        """
        self._database.connect()

    def begin(self) -> None:
        """
        Begins a new transaction.

        This method must be called before making changes that need to be committed or rolled back.
        """
        self._database.begin()

    def save(self) -> None:
        """
        Commits the current transaction and saves changes to the database.

        This method should be called to persist any changes made during the transaction.
        """
        self._database.commit()

    def rollback(self) -> None:
        """
        Rolls back the current transaction and reverts the database state to the last commit point.

        This method should be called if an error occurs or if the transaction needs to be aborted.
        """
        self._database.rollback()

    def close(self) -> None:
        """
        Closes the database connection.

        This method should be called when all database operations are complete to release resources.
        """
        self._database.close()
