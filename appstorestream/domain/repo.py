#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/domain/repo.py                                                      #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 10:29:30 pm                                                 #
# Modified   : Sunday July 28th 2024 09:06:18 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Domain Repository Module"""
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

import pandas as pd

from appstorestream.application.base.repo import AppLayerRepo

# ------------------------------------------------------------------------------------------------ #
T = TypeVar('T')  # Define a generic type variable
# ------------------------------------------------------------------------------------------------ #
#                                   DOMAIN LAYER REPO                                              #
# ------------------------------------------------------------------------------------------------ #
class DomainLayerRepo(ABC, Generic[T]):
    """Base class for domain layer repositories.

    This class serves as an abstract base class for repositories that handle
    domain-specific data. It provides methods for fetching, adding, upserting,
    and deleting data in the repository.

    Attributes:
        None
    """

    @abstractmethod
    def get(self, category_id: int, **kwargs: Any) -> pd.DataFrame:
        """Fetches data by category ID and returns a DataFrame.

        Args:
            category_id (int): The ID of the category to fetch data for.
            **kwargs (Any): Additional keyword arguments for customizing the query.

        Returns:
            pd.DataFrame: A DataFrame containing the data for the specified category.
        """
        pass


    @abstractmethod
    def upsert(self, data: pd.DataFrame) -> None:
        """Performs an upsert operation on the data in the repository.

        Upsert is a combination of insert and update. If the data already exists
        in the repository, it will be updated; otherwise, it will be inserted.

        Args:
            data (pd.DataFrame): A DataFrame containing the data to be upserted into the repository.

        Returns:
            None
        """
        pass
# ------------------------------------------------------------------------------------------------ #
#                                   UNIT OF WORK BASE CLASS                                        #
# ------------------------------------------------------------------------------------------------ #
class UnitOfWork(ABC):
    @abstractmethod
    @property
    def appdata_repo(self)  -> DomainLayerRepo:
        """Returns an appdata repository"""

    @abstractmethod
    @property
    def review_repo(self)  -> DomainLayerRepo:
        """Returns an review repository"""

    @abstractmethod
    @property
    def project_repo(self)  -> AppLayerRepo:
        """Returns an project repository"""

    @abstractmethod
    @property
    def job_repo(self)  -> AppLayerRepo:
        """Returns an job repository"""