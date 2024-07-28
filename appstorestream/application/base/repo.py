#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/base/repo.py                                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 01:45:00 am                                                   #
# Modified   : Friday July 26th 2024 04:43:56 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Job Repo Module"""
import json
from abc import abstractmethod
from typing import Generic, TypeVar

import redis

from appstorestream.application.base.service import Service

# ------------------------------------------------------------------------------------------------ #
T = TypeVar('T')
# ------------------------------------------------------------------------------------------------ #
class AppLayerRepo(Service, Generic[T]):
    """Base class for application layer repositories.

    This class serves as an abstract base class for repositories that handle
    application-specific data. It provides methods for fetching, adding, updating,
    and deleting entities in the repository.
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    @abstractmethod
    def add(self, job: T) -> None:
        """Adds a job to the repository."""
        pass

    @abstractmethod
    def get(self, job_id: str) -> T:
        """Fetches a job by its ID."""
        pass

    @abstractmethod
    def update(self, job: T) -> None:
        """Updates a job in the repository."""
        pass

    @abstractmethod
    def delete(self, job_id: str) -> None:
        """Deletes a job from the repository."""
        pass