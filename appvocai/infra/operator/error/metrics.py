#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/operator/error/metrics.py                                           #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 09:04:54 pm                                               #
# Modified   : Wednesday September 4th 2024 06:24:00 pm                                            #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Error Metrics Module"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from appvocai.infra.monitor.metrics import Metrics

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------ #
class ErrorType(Enum):
    """
    Enumeration representing various types of errors that can occur during different
    stages of data processing, such as extraction, transformation, and loading.

    Attributes:
        SWITCH_PROXY (int): Error code for proxy switch required.
        PERMANENT_REDIRECT (int): Error code for permanent redirection.
        BAD_REQUEST (int): Error code for bad requests (client-side error).
        NOT_FOUND (int): Error code when a requested resource is not found.
        NOT_ACCEPTABLE (int): Error code for unacceptable requests.
        REQUEST_TIMEOUT (int): Error code for request timeouts.
        TOO_MANY_REQUESTS (int): Error code when too many requests are sent in a given timeframe.
        CLIENT_CLOSED_REQUEST (int): Error code when the client closes the request.
        CLIENT_ERRORS (int): General client-side error code (4xx).
        INTERNAL_SERVER_ERROR (int): General server-side error code (5xx).
        BAD_GATEWAY (int): Error code for bad gateway responses.
        SERVICE_UNAVAILABLE (int): Error code when the service is unavailable.
        GATEWAY_TIMEOUT (int): Error code for gateway timeouts.
        CONNECTION_TIMED_OUT (int): Error code for connection timeouts.
        A_TIMEOUT_OCCURRED (int): Error code when a timeout occurs.
        SITE_IS_OVERLOADED (int): Error code when the site is overloaded.
        NETWORK_CONNECT_TIMEOUT_ERROR (int): Error code for network connection timeouts.
        SERVER_ERRORS (int): General server-side error code (5xx).
        REDIRECTION (int): General redirection error code (3xx).
        DATABASE_ERROR (int): Error code for database-related errors.
        TRANSFORM_ERROR (int): Error code for transformation-related errors.
        LOAD_ERROR (int): Error code for loading-related errors.
    """

    SWITCH_PROXY = 306
    PERMANENT_REDIRECT = 308
    BAD_REQUEST = 400
    NOT_FOUND = 404
    NOT_ACCEPTABLE = 406
    REQUEST_TIMEOUT = 408
    TOO_MANY_REQUESTS = 429
    CLIENT_CLOSED_REQUEST = 499
    CLIENT_ERRORS = 400
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    CONNECTION_TIMED_OUT = 522
    A_TIMEOUT_OCCURRED = 524
    SITE_IS_OVERLOADED = 529
    NETWORK_CONNECT_TIMEOUT_ERROR = 599
    SERVER_ERRORS = 500
    REDIRECTION = 300
    DATABASE_ERROR = 1000
    TRANSFORM_ERROR = 2000
    LOAD_ERROR = 3000
    UNKNOWN_ERROR = 4000

    @classmethod
    def from_operator_and_code(cls, operator: str, error_code: int) -> "ErrorType":
        """
        Factory method to return an ErrorType enum instance based on the provided operator name and error code.

        This method attempts to find an exact match for the error code in the enum. If no match is found,
        it will determine the appropriate error type based on the operator.

        For extract-related operators, the error code is rounded to the nearest hundred and mapped to
        general error categories (e.g., 3xx for redirection, 4xx for client errors, 5xx for server errors).

        Args:
            operator (str): The name of the operator (e.g., "ASession", "TransformAppData").
            error_code (int): The numeric error code to be mapped to an ErrorType.

        Returns:
            ErrorType: The corresponding ErrorType enum instance.

        Raises:
            ValueError: If no matching error type can be found for the given operator and error code.
        """
        operator_lower = operator.lower()

        # Try to find the exact error code first
        for member in cls:
            if member.value == error_code:
                return member

        # If not found, handle based on operator type
        if "extract" in operator_lower:
            rounded_error_code = round(error_code, -2)
            if rounded_error_code == 300:
                return cls.REDIRECTION
            elif rounded_error_code == 400:
                return cls.CLIENT_ERRORS
            elif rounded_error_code == 500:
                return cls.SERVER_ERRORS
            else:
                raise ValueError(
                    f"No enum found for operator: {operator} and error_code: {error_code}"
                )
        elif "transform" in operator_lower:
            return cls.TRANSFORM_ERROR
        elif "load" in operator_lower:
            return cls.LOAD_ERROR
        else:
            raise ValueError(
                f"No enum found for operator: {operator} and error_code: {error_code}"
            )


@dataclass
class MetricsError(Metrics):
    """
    MetricsError class for gathering and computing error-related metrics in data processing tasks.

    Attributes:
        operator (str): The name of the operator class where the error occurred.
        error_code (int): The numeric error code representing the specific error.
        error_type (Optional[ErrorType]): The type of error, as determined by the ErrorType enum.
    """

    operator: str = ""  # The name of the operator class
    error_code: int = 0  # Numeric error code
    error_type: ErrorType = (
        ErrorType.UNKNOWN_ERROR
    )  # Defaults to unknown to provide a valid value.
    retries: int = 0  # Number of retries.

    def compute(self, operator: str, error_code: int) -> Any:
        """
        Computes additional metrics based on the provided operator and error code.

        This method assigns the provided operator and error code to the instance and determines the
        error type using the ErrorType.from_operator_and_code method.

        Args:
            operator (str): The name of the operator class where the error occurred.
            error_code (int): The numeric error code representing the specific error.
        """
        self.operator = operator
        self.error_code = error_code
        self.error_type = ErrorType.from_operator_and_code(
            operator=operator, error_code=error_code
        )

    def validate(self) -> None:
        """
        Validates the error metrics to ensure all required fields are correctly populated.

        This method checks whether the operator, error_code, and error_type fields are non-null and
        raises a RuntimeError with a descriptive message if any of these validations fail.

        Raises:
            RuntimeError: If any of the required fields (operator, error_code, error_type) are invalid or null.
        """
        if not self.operator:
            msg = "Operator must be non-null."
            logger.exception(msg)
            raise RuntimeError(msg)
        if not self.error_code:
            msg = "Error code must be non-null"
            logger.exception(msg)
            raise RuntimeError(msg)
        if not self.error_type:
            msg = "Error type must be non-null"
            logger.exception(msg)
            raise RuntimeError(msg)
        if not isinstance(self.error_type, ErrorType):
            msg = "Error type must be a valid ErrorType."
            logger.exception(msg)
            raise RuntimeError(msg)
