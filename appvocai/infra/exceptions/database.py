#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/exceptions/database.py                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 06:39:15 pm                                               #
# Modified   : Saturday August 31st 2024 06:40:26 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Custom Database exception class module."""
from typing import Optional


# ------------------------------------------------------------------------------------------------ #
class DatabaseError(Exception):
    """
    Custom exception for database-related errors.

    This exception is raised when an error occurs during a database operation, such as a failed
    query, connection issues, or data integrity problems. It allows for more specific exception
    handling in the application, particularly for operations involving database interactions.

    Args:
        message (str): A descriptive message explaining the error.
        original_exception (Optional[Exception], optional): The original exception that caused this error,
                                                           if applicable. Defaults to None.
    """

    def __init__(self, message: str, original_exception: Optional[Exception] = None) -> None:
        super().__init__(message)
        self.original_exception: Optional[Exception] = original_exception

    def __str__(self) -> str:
        if self.original_exception:
            return f"{self.__class__.__name__}: {self.args[0]} (caused by {self.original_exception})"
        return f"{self.__class__.__name__}: {self.args[0]}"
