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
# Modified   : Sunday July 28th 2024 01:47:45 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Job Repo Module"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# ------------------------------------------------------------------------------------------------ #
T = TypeVar('T')
# ------------------------------------------------------------------------------------------------ #
class AppLayerRepo(ABC, Generic[T]):
    """Base class for application layer repositories.

    This class serves as an abstract base class for repositories that handle
    application-specific data. It provides methods for fetching, adding, updating,
    and deleting entities in the repository.
    """

    @abstractmethod
    def add(self, entity: T) -> None:
        """Adds an entity to the repository."""
        pass

    @abstractmethod
    def get(self, id: int) -> T:
        """Fetches an entity by its ID."""
        pass

    @abstractmethod
    def update(self, entity: T) -> None:
        """Updates a job in the repository."""
        pass

