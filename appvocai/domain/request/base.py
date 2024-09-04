#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/request/base.py                                                    #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday August 26th 2024 10:23:34 pm                                                 #
# Modified   : Tuesday September 3rd 2024 08:42:16 pm                                              #
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

from appvocai.core.data import DataClass
from appvocai.core.enum import ContentType

# ------------------------------------------------------------------------------------------------ #
T = TypeVar("T", bound="Request")
U = TypeVar("U", bound="RequestAsync[Request]")


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Entity(DataClass):
    """Defines a base class for appdata and appreview classes."""


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Request(DataClass):
    """Abstract base class for batch HTTP requests"""

    id: str = ""  # System generated UUID (default: "")
    date_time: Optional[datetime] = None  # Datetime the request was sent.
    method: str = "GET"  # The HTTP method used (GET, POST, etc.) (default: 'GET')

    def __post_init__(self) -> None:
        self.id = str(uuid4())

    @property
    @abstractmethod
    def headers(self) -> Union[Collection[str], Dict[str, Any]]:
        """Returns a headers dictionary if designated."""

    @property
    @abstractmethod
    def baseurl(self) -> str:
        """Base URL for requests"""

    @property
    @abstractmethod
    def params(self) -> Dict[str, Any]:
        """HTTP REquest Parameters"""

    @property
    @abstractmethod
    def start_index(self) -> int:
        """Starting index for the request."""

    @property
    @abstractmethod
    def end_index(self) -> int:
        """Ending index for the request."""

    @property
    @abstractmethod
    def content_type(self) -> ContentType:
        """Indicates the type of content for which the request is made."""


# ------------------------------------------------------------------------------------------------ #
@dataclass
class RequestAsync(DataClass, Generic[T]):
    """Encapsulates a list of requests"""

    n: int = 0
    requests: List[T] = field(default_factory=list)

    def add_request(self, request: T) -> None:
        self.n += 1
        self.requests.append(request)


# ------------------------------------------------------------------------------------------------ #
class RequestGen(ABC, Generic[U]):

    @abstractmethod
    def __iter__(self) -> RequestGen[U]:
        """Initalizes the generation of Requests"""

    @abstractmethod
    def __next__(self) -> U:
        """Generates the next request"""
