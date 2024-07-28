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
# Modified   : Friday July 26th 2024 04:35:38 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Domain Repository Module"""
from abc import ABC, abstractmethod
from typing import Any, Generic, List, TypeVar

import pandas as pd

# ------------------------------------------------------------------------------------------------ #
T = TypeVar('T')  # Define a generic type variable
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
    def add(self, data: pd.DataFrame) -> None:
        """Adds data to the repository.

        Args:
            data (pd.DataFrame): A DataFrame containing the data to be added to the repository.

        Returns:
            None
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

    @abstractmethod
    def delete(self, category_id: int, **kwargs: Any) -> None:
        """Deletes data from the repository by category ID.

        Args:
            category_id (int): The ID of the category whose data should be deleted.
            **kwargs (Any): Additional keyword arguments for customizing the delete operation.

        Returns:
            None
        """
        pass