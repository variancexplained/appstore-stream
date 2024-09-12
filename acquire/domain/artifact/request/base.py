#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /acquire/domain/artifact/request/base.py                                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday August 26th 2024 10:23:34 pm                                                 #
# Modified   : Monday September 9th 2024 04:57:55 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Collection, Dict, Generic, List, Optional, TypeVar, Union

from acquire.domain.artifact.base import Artifact

# ------------------------------------------------------------------------------------------------ #
T = TypeVar("T", bound="Request")
U = TypeVar("U", bound="AsyncRequest[Request]")


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Request(Artifact):
    """
    Abstract base class for individual HTTP requests, inheriting from the Artifact class.

    This class provides a base structure for managing HTTP requests as artifacts within the system.
    Each request is tied to a specific task via the `task_passport` and handles request-level attributes
    like HTTP method, sent time, and abstract methods to define request-specific details like headers,
    base URL, and parameters.

    Inherited Attributes from Artifact:
        entype (DataType): The type of the entity, distinguishing between different stage types.
        id (str): A unique identifier for the entity.
        created (Optional[datetime]): The timestamp when the entity was initially created.
        modified (Optional[datetime]): The timestamp when the entity was last modified.
        environment (Optional[Env]): The environment in which the entity operates (e.g., Development, Production).
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

    def __init__(self, *args: Any, **kwargs: Dict[str, Any]) -> None:
        """
        Initializes the Request object, inheriting from Artifact and associating the request with a task.

        Args:
            task_passport (TaskPassport): The passport of the task associated with this request.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """


# ------------------------------------------------------------------------------------------------ #
@dataclass
class AsyncRequest(Artifact, Generic[T]):
    """
    A class representing a batch of asynchronous requests, inheriting from Artifact.

    This class manages a collection of asynchronous requests, tracking the number of requests
    and providing methods to add new requests to the batch. It ensures the modified timestamp is
    updated whenever a request is added.

    Inherited Attributes from Artifact:
        entype (DataType): The type of the entity, distinguishing between different stage types.
        id (str): A unique identifier for the entity.
        created (Optional[datetime]): The timestamp when the entity was initially created.
        modified (Optional[datetime]): The timestamp when the entity was last modified.
        environment (Optional[Env]): The environment in which the entity operates (e.g., Development, Production).
        version (str): The version of the entity or schema, defaulting to "0.1.0".
        tags (List[str]): A list of tags associated with the entity for categorization or labeling.

    Attributes:
        request_count (int): The number of requests in the batch. Defaults to 0.
        requests (List[T]): A list of requests in the batch.

    Methods:
        add_request(request: T) -> None:
            Adds a new request to the list of requests and updates the modified timestamp.
    """

    request_count: int = 0
    requests: List[T] = field(default_factory=list)

    def __init__(self) -> None:
        """
        Initializes the AsyncRequest object, associating it with a task.

        Args:
            task_passport (TaskPassport): The passport of the task associated with this batch of requests.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """

    def add_request(self, request: T) -> None:
        """
        Adds a request to the list of requests, increments the request count,
        and updates the modified timestamp.

        Args:
            request (T): The request to be added to the list of requests.
        """
        self.request_count += 1
        self.requests.append(request)


# ------------------------------------------------------------------------------------------------ #
class RequestGen(ABC, Generic[U]):
    """
    Abstract base class for generating requests asynchronously.

    This class serves as a generator for requests, implementing the iterator protocol
    with `__iter__` and `__next__` methods that are meant to be implemented by subclasses.
    It associates each generated request with a specific task via the `task_passport`.

    Abstract Methods:
        __iter__() -> RequestGen[U]:
            Initializes the generation of requests, making the class iterable.
        __next__() -> U:
            Generates the next request in the sequence.
    """

    @abstractmethod
    def __iter__(self) -> RequestGen[U]:
        """Initializes the generation of requests, making the class iterable."""

    @abstractmethod
    def __next__(self) -> U:
        """Generates the next request in the sequence."""
