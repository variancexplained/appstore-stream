#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/artifact/response/response.py                                      #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday August 27th 2024 10:27:49 am                                                #
# Modified   : Saturday September 7th 2024 07:40:55 pm                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from aiohttp import ClientResponse, ClientResponseError
from pympler import asizeof

from appvocai.core.data import DataClass
from appvocai.domain.artifact.base import Artifact
from appvocai.infra.identity.passport import OperationPassport

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class AsyncResponse(Artifact):
    """
    A collection of Request/Response objects resulting from an asynchronous request.

    This class holds the results of an asynchronous operation, specifically a list of response objects
    generated from the requests made. It keeps track of the total number of responses and allows adding
    new responses to the collection.

    Attributes:
    -----------
    response_count : int
        The total number of responses collected from the asynchronous operation. Default is 0.
    responses : List[Response]
        A list of `Response` objects, each representing the result of an individual request in the asynchronous
        operation. Initialized as an empty list by default.

    Methods:
    --------
    __init__(operation_passport: OperationPassport) -> None
        Initializes the `AsyncResponse` object with an `OperationPassport`, inherited from the `Artifact` class.

    add_responses(responses: List[Response]) -> None
        Adds a list of `Response` objects to the `AsyncResponse` and updates the `response_count` accordingly.

    Parameters:
    -----------
    operation_passport : OperationPassport
        An object representing the passport of the operation, which contains metadata about the operation, task,
        and project related to the responses.
    """

    response_count: int = 0
    responses: List[Response] = field(default_factory=list)

    def __init__(self, operation_passport: OperationPassport) -> None:
        """
        Initializes the `AsyncResponse` with an `OperationPassport`, which provides the context for the
        asynchronous operation.

        Parameters:
        -----------
        operation_passport : OperationPassport
            Metadata related to the operation that generated the responses, including task and project IDs,
            data type, and category.
        """
        super().__init__(operation_passport=operation_passport)

    def add_responses(self, responses: List[Response]) -> None:
        """
        Adds a list of `Response` objects to the `AsyncResponse` collection and updates the response count.

        Parameters:
        -----------
        responses : List[Response]
            A list of `Response` objects to be added to the collection.

        The `response_count` is updated to reflect the number of responses added.
        """
        self.response_count = len(responses)
        self.responses: List[Response] = responses


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ResponseHeaders(DataClass):
    """
    A class to represent the HTTP response headers and related metadata from a server response.

    This class extracts and stores important server and response metadata, such as the server name,
    the HTTP status code, the size of the response content, and the timestamps for when the request
    was processed by the server and received by the client.

    Attributes:
    -----------
    server : str
        The name of the server from which the response originated (default: empty string).
    server_datetime : Optional[datetime]
        The datetime when the server processed the request, parsed from the "Date" header (default: None).
    connection : str
        Information about how the connection was dispatched (e.g., keep-alive or close) (default: empty string).
    status : int
        The HTTP status code of the response (default: 0).
    size : int
        The size of the content in the response, in bytes (default: 0).
    response_datetime : Optional[datetime]
        The datetime when the client received the response (default: None).

    Methods:
    --------
    __init__(response: ClientResponse) -> None
        Initializes the `ResponseHeaders` object by extracting relevant metadata from the given `ClientResponse` object.

    parse_date(date_str: str) -> Optional[datetime]
        A helper method to parse a date string from the response headers into a `datetime` object.
        If the date is not present or cannot be parsed, it returns `None`.

    parse_size(response: ClientResponse) -> int
        A helper method to extract and calculate the size of the response content. It first attempts
        to retrieve the size from the `Content-Length` header. If this is not present, it tries to
        infer the size based on the JSON content or the response itself. If all else fails, it logs
        a warning and returns 0.
    """

    # 1. Server Metadata
    server: str = ""  # The endpoint server (default: "")
    server_datetime: Optional[datetime] = (
        None  # Datetime the server processed the request (default: None)
    )

    connection: str = ""  # How the connection is dispatched (default: "")

    # 2. Response Metadata
    status: int = 0  # The HTTP return code (default: 0)
    size: int = 0  # Size of content in response in bytes (default: 0)
    response_datetime: Optional[datetime] = (
        None  # Datetime the request was received (default: None)
    )

    def __init__(self, response: ClientResponse) -> None:
        """
        Initializes the `ResponseHeaders` object by extracting metadata from the `ClientResponse`.

        Parameters:
        -----------
        response : ClientResponse
            The response object from which to extract headers and other metadata, such as status code,
            server name, content length, and date.

        The initialization method assigns the server name, connection type, status code, content size,
        and the server processing date. It also captures the time the response was received by the client.
        """
        # 1 Server Metadata
        self.server = response.headers.get("Server", "")
        self.server_datetime = self.parse_date(
            date_str=response.headers.get("Date", "")
        )
        self.connection = response.headers.get("Connection", "")

        # 2 Response Metadata
        self.status = response.status
        self.size = self.parse_size(response=response)
        self.response_datetime = datetime.now()

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parses the date from the response headers into a `datetime` object.

        Parameters:
        -----------
        date_str : str
            The date string extracted from the response headers (typically the "Date" header).

        Returns:
        --------
        Optional[datetime]
            A `datetime` object representing the parsed date, or `None` if the string is empty
            or the parsing fails.
        """
        if date_str:
            return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S GMT")
        return None

    def parse_size(self, response: ClientResponse) -> int:
        """
        Extracts and calculates the size of the response content using Pympler's asizeof for accurate measurement.

        Parameters:
        -----------
        response : ClientResponse
            The response object from which to calculate the size.

        Returns:
        --------
        int
            The total size of the response content in bytes. It first tries to use the 'Content-Length'
            header, and if that is missing, it calculates the full memory size of the response object
            using Pympler's asizeof to include all referenced objects.
        """
        try:
            # First try to get size from Content-Length header
            return int(response.headers["Content-Length"])
        except KeyError:
            # If Content-Length is not provided, calculate the full size using Pympler
            try:
                return int(asizeof.asizeof(response.json(content_type=None)))  # type: ignore
            except ClientResponseError:
                return int(
                    asizeof.asizeof(response)  # type: ignore
                )  # Fall back to full response object size
            except Exception:
                logger.warning("Content length not provided and could not be inferred.")
                return 0


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Response(Artifact):
    """
    Represents an HTTP response, containing the headers, content, and metadata such as timestamps and latency.

    The `Response` class captures the full details of an HTTP response, including the headers, content,
    the time the request was sent, the time it was received, and the resulting latency. It supports parsing
    both headers and content from an asynchronous `ClientResponse` and includes mechanisms for recording
    when the response is sent and received.

    Attributes:
    -----------
    headers : ResponseHeaders
        An object containing the parsed HTTP response headers.
    content : Union[List[Dict[str, Any]], Dict[str, Any]]
        The content of the HTTP response, which can be either a dictionary or a list of dictionaries, depending
        on the response body.
    dt_sent : Optional[datetime]
        The timestamp representing when the request was sent (default: None).
    dt_recv : Optional[datetime]
        The timestamp representing when the response was received (default: None).
    latency : float
        The time difference (in seconds) between when the request was sent and when the response was received
        (default: 0).

    Methods:
    --------
    __init__(operation_passport: OperationPassport) -> None
        Initializes the `Response` object and links it to the given `OperationPassport`, inheriting from `Artifact`.

    async parse_response(response: ClientResponse) -> None
        Asynchronously parses both the headers and content of the `ClientResponse` and updates the `Response` object.

    _parse_header(response: ClientResponse) -> ResponseHeaders
        Extracts and returns the HTTP headers from the `ClientResponse` as a `ResponseHeaders` object.

    async _parse_content(response: ClientResponse) -> Union[List[Dict[str, Any]], Dict[str, Any]]
        Asynchronously parses and returns the content of the `ClientResponse`, which can be either a dictionary
        or a list of dictionaries, depending on the response format.

    Parameters:
    -----------
    operation_passport : OperationPassport
        The passport that contains metadata related to the operation, such as task and project information.
    """

    headers: ResponseHeaders
    content: Union[List[Dict[str, Any]], Dict[str, Any]]

    def __init__(self, operation_passport: OperationPassport) -> None:
        """
        Initializes the `Response` object with an `OperationPassport`, setting up the metadata context.

        Parameters:
        -----------
        operation_passport : OperationPassport
            Metadata related to the operation, which includes information such as task ID, job ID, and category.
        """
        super().__init__(operation_passport=operation_passport)

    async def parse_response(self, response: ClientResponse) -> None:
        """
        Asynchronously parses the `ClientResponse` object, extracting both headers and content.

        Parameters:
        -----------
        response : ClientResponse
            The HTTP response object to be parsed.

        This method first parses the headers, then asynchronously parses the content of the response.
        """
        self.headers = self._parse_header(response=response)
        self.content = await self._parse_content(response=response)

    def _parse_header(self, response: ClientResponse) -> ResponseHeaders:
        """
        Parses the HTTP response headers and returns a `ResponseHeaders` object.

        Parameters:
        -----------
        response : ClientResponse
            The HTTP response object from which to extract headers.

        Returns:
        --------
        ResponseHeaders
            An object containing parsed HTTP response header metadata such as server, connection, and date.
        """
        return ResponseHeaders(response=response)

    async def _parse_content(
        self, response: ClientResponse
    ) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Asynchronously parses the content of the HTTP response and returns it as a dictionary or list of dictionaries.

        Parameters:
        -----------
        response : ClientResponse
            The HTTP response object from which to extract content.

        Returns:
        --------
        Union[List[Dict[str, Any]], Dict[str, Any]]
            The parsed content of the response, which could be either a dictionary or a list of dictionaries,
            depending on the structure of the response body.
        """
        content: Union[Dict[str, Any], List[Dict[str, Any]]] = await response.json(
            content_type=None
        )
        return content
