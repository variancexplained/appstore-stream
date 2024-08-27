#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/response/base.py                                                   #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday August 27th 2024 10:27:49 am                                                #
# Modified   : Tuesday August 27th 2024 06:39:44 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TypeVar
from uuid import uuid4

from aiohttp import ClientResponse

from appvocai.core.data import DataClass
from appvocai.domain.request.base import Request

# ------------------------------------------------------------------------------------------------ #
T = TypeVar('T', bound='Response')
# ------------------------------------------------------------------------------------------------ #
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class Response(DataClass):
    """Abstract base class for Responses.

    Attributes:
        id (str): System generated UUID. Default is an empty string.
        request_uuid (str): Endpoint's request UUID if available. Default is an empty string.
        request_datetime (datetime): Datetime the request was sent. Default is None.
        request_type (str): Indicates the type of request, such as 'AppData' or 'AppReview'. Default is an empty string.
        method (str): The HTTP method used (GET, POST, etc.). Default is 'GET'.
        endpoint (str): The URL or endpoint being accessed. Default is an empty string.
        index (int): The index or offset requested. Default is 0.

        server (str): The endpoint server. Default is an empty string.
        server_datetime (datetime): Datetime the server processed the request. Default is None.
        cache_control (str): Cache control information. Default is an empty string.
        x_cache (str): Information on caching behavior (e.g., X-Cache or X-Cache-Remote). Default is an empty string.
        strict_transport_security (str): Security feature for HTTPS communication (e.g., Strict-Transport-Security). Default is an empty string.
        connection (str): Indicates how the connection is dispatched (e.g., keep-alive or close). Default is an empty string.
        vary (str): Specifies the fields that might vary in responses (e.g., Vary). Default is an empty string.

        status (int): The HTTP return code. Default is 0.
        n (int): The number of records returned. Default is 0.
        content_type (str): Type of HTTP content returned (e.g., application/json). Default is an empty string.
        content_length (str): Size of content in response in bytes. Default is an empty string.
        encoding (str): Encoding used for the response (e.g., utf-8). Default is an empty string.
        response_datetime (datetime): Datetime the request was received. Default is None.
        latency (float): The latency of the request in seconds. Default is 0.0.
    """

    # 1. Request Metadata
    id: str = ""  # System generated UUID (default: "")
    request_uuid: str = ""  # Endpoint's request UUID if available (default: "")
    request_datetime: datetime = None  # Datetime the request was sent (default: None)
    request_type: str = ""  # Indicates the type of request, e.g., 'AppData' or 'AppReview' (default: "")
    method: str = 'GET'  # The HTTP method used (GET, POST, etc.) (default: 'GET')
    endpoint: str = ""  # The URL or endpoint being accessed (default: "")
    start_index: int = 0  # The index or offset requested (default: 0)
    end_index: int = 0  # The index or offset requested (default: 0)

    # 2. Server Metadata
    server: str = ""  # The endpoint server (default: "")
    server_datetime: datetime = None  # Datetime the server processed the request (default: None)
    cache_control: str = ""  # Cache control information (default: "")
    x_cache: str = ""  # Information on caching behavior (X-Cache or X-Cache-Remote) (default: "")
    strict_transport_security: str = ""  # Security feature for HTTPS communication (default: "")
    connection: str = ""  # How the connection is dispatched (default: "")
    vary: str = ""  # Specifies fields that might vary in responses (default: "")

    # 3. Response Metadata
    status: int = 0  # The HTTP return code (default: 0)
    n: int = 0  # The number of records returned (default: 0)
    content_type: str = ""  # Type of HTTP content returned (default: "")
    content_length: str = ""  # Size of content in response in bytes (default: "")
    encoding: str = ""  # Encoding used for the response (default: "")
    response_datetime: datetime = None  # Datetime the request was received (default: None)
    latency: float = 0.0  # The latency of the request in seconds (default: 0.0)

    def __post_init__(self) -> None:
        self.id = str(uuid4())

    def parse_request(self, request: Request) -> None:
        """Parses the request object and sets the request-related member variables.

        Args:
            request (Request): The request object containing relevant metadata.
        """
        # Set request metadata
        self.request_uuid = request.id
        self.request_datetime = request.date_time
        self.request_type = "override_in_baseclass"
        self.endpoint = request.baseurl
        self.start_index = request.start_index
        self.end_index = request.end_index

    async def parse_response(self, response: ClientResponse) -> None:
        """Parses the response object from aiohttp and sets the member variables.

        Args:
            response (ClientResponse): The response object from the HTTP request.

        Updates:
            - request_uuid: Extracted from response headers if available.
            - server: Extracted from the 'Server' header if available.
            - server_datetime: Extracted from the 'Date' header if available.
            - cache_control: Extracted from the 'Cache-Control' header if available.
            - x_cache: Extracted from the 'X-Cache' header if available.
            - strict_transport_security: Extracted from the 'Strict-Transport-Security' header if available.
            - connection: Extracted from the 'Connection' header if available.
            - vary: Extracted from the 'Vary' header if available.
            - status: HTTP return code from the response object.
            - n: Number of records returned (if applicable).
            - content_type: Extracted from the 'Content-Type' header if available.
            - content_length: Extracted from the 'Content-Length' header if available.
            - encoding: Extracted from the 'Content-Encoding' header if available.
            - response_datetime: The current datetime when the response is processed.
        """
        # Override request metadata if available
        self.request_uuid = response.headers.get('x-apple-request-uuid', self.request_uuid)

        # Set server metadata
        self.server = response.headers.get('Server', self.server)
        self.server_datetime = self.parse_date(response.headers.get('Date', None))  # Only this needs conversion
        self.cache_control = response.headers.get('Cache-Control', self.cache_control)
        self.x_cache = response.headers.get('X-Cache', response.headers.get('X-Cache-Remote', None))
        self.strict_transport_security = response.headers.get('Strict-Transport-Security', self.strict_transport_security)
        self.connection = response.headers.get('Connection', self.connection)
        self.vary = response.headers.get('Vary', self.vary)

        # Set response metadata
        self.status = response.status
        self.n = response.headers.get('n', self.n)  # Placeholder for logic to determine number of records
        self.content_type = response.headers.get('Content-Type', self.content_type)
        self.content_length = response.headers.get('Content-Length', self.content_length)
        self.encoding = response.headers.get('Content-Encoding', self.encoding)
        self.response_datetime = datetime.now(timezone.utc)  # Current datetime in GMT
        self.latency = self.calculate_latency()

        # Logging the values after parsing
        logging.debug(f"Parsed Response - Status: {self.status}, n: {self.n}, Content-Type: {self.content_type}, "
                    f"Response Datetime: {self.response_datetime}, Server: {self.server}, "
                    f"Request UUID: {self.request_uuid}, Cache-Control: {self.cache_control}")

    def parse_date(self, date_str: str) -> datetime:
        """Helper method to parse the date from the response headers."""
        if date_str:
            return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')
        return None

    def calculate_latency(self) -> float:
        """Computes latency from request and response times."""
        return (self.response_datetime - self.request_datetime).total_seconds()
