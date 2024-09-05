#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/openty/request/base.py                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday August 26th 2024 10:23:34 pm                                                 #
# Modified   : Thursday September 5th 2024 06:58:10 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Collection, Dict, Generic, List, Optional, TypeVar, Union
from uuid import uuid4

from appvocai.core.identity import Openty

# ------------------------------------------------------------------------------------------------ #
T = TypeVar("T", bound="Request")
U = TypeVar("U", bound="RequestAsync[Request]")


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Request(Openty, ABC):
    """
    Abstract base class for individual HTTP requests, inheriting from the Openty class.

    Inherited Attributes from Openty:
        entype (DataType): The type of the entity, distinguishing between different operation types.
        id (str): A unique identifier for the entity.
        created (Optional[datetime]): The timestamp when the entity was initially created.
        modified (Optional[datetime]): The timestamp when the entity was last modified.
        environment (Optional[Env]): The environment in which the entity operates (e.g., Development, Production),
                                     determined automatically based on configuration.
        version (str): The version of the entity or schema, defaulting to "0.1.0".
        tags (List[str]): A list of tags associated with the entity for categorization or labeling.

    Attributes:
        sent (Optional[datetime]): The datetime when the request was sent. Defaults to None.
        method (str): The HTTP method used for the request (e.g., GET, POST). Defaults to "GET".

    Abstract Methods:
        headers: Returns a collection or dictionary representing the headers for the HTTP request.
        baseurl: Returns the base URL for the HTTP request.
        params: Returns a dictionary of parameters to be included in the HTTP request.
        start_index: Returns the starting index for the request, if applicable.
        end_index: Returns the ending index for the request, if applicable.
    """

    sent: Optional[datetime] = None  # Datetime the request was sent.
    method: str = "GET"  # The HTTP method used (GET, POST, etc.) (default: 'GET')
    metrics: Metrics

    @property
    @abstractmethod
    def headers(self) -> Union[Collection[str], Dict[str, Any]]:
        """Returns a collection or dictionary representing the headers for the HTTP request."""

    @property
    @abstractmethod
    def baseurl(self) -> str:
        """Returns the base URL for the HTTP request."""

    @property
    @abstractmethod
    def params(self) -> Dict[str, Any]:
        """Returns a dictionary of parameters to be included in the HTTP request."""

    @property
    @abstractmethod
    def start_index(self) -> int:
        """Returns the starting index for the request, if applicable."""

    @property
    @abstractmethod
    def end_index(self) -> int:
        """Returns the ending index for the request, if applicable."""


# ------------------------------------------------------------------------------------------------ #
@dataclass
class RequestAsync(Openty, Generic[T]):
    """
    Encapsulates a list of asynchronous requests, inheriting from the Openty class.

    Inherited Attributes from Openty:
        entype (DataType): The type of the entity, distinguishing between different operation types.
        id (str): A unique identifier for the entity, generated automatically if not provided.
        created (Optional[datetime]): The timestamp when the entity was initially created.
        modified (Optional[datetime]): The timestamp when the entity was last modified.
        environment (Optional[Env]): The environment in which the entity operates (e.g., Development, Production),
                                     determined automatically based on configuration.
        version (str): The version of the entity or schema, defaulting to "0.1.0".
        tags (List[str]): A list of tags associated with the entity for categorization or labeling.
        size: Method inherited from Openty that calculates the total size of the object, including its attributes.

    Attributes:
        request_count (int): The number of requests contained within this object. Defaults to 0.
        requests (List[T]): A list of requests of type T, which is a generic type parameter. Defaults to an empty list.

    Methods:
        __post_init__: Initializes the entity by generating a unique ID and setting the current timestamp.
        add_request: Adds a request to the list of requests, increments the request count, and updates the modified timestamp.
    """

    request_count: int = 0
    requests: List[T] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initializes the entity after dataclass construction."""
        self.id = str(uuid4())
        self.created = datetime.now()

    def add_request(self, request: T) -> None:
        """
        Adds a request to the list of requests, increments the request count,
        and updates the modified timestamp.

        Args:
            request (T): The request to be added to the list of requests.
        """
        self.request_count += 1
        self.modified = datetime.now()
        self.requests.append(request)


# ------------------------------------------------------------------------------------------------ #
class RequestGen(ABC, Generic[U]):

    @abstractmethod
    def __iter__(self) -> RequestGen[U]:
        """Initalizes the generation of Requests"""

    @abstractmethod
    def __next__(self) -> U:
        """Generates the next request"""


# ------------------------------------------------------------------------------------------------ #
# %%
