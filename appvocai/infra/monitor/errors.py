#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/monitor/errors.py                                                   #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday September 7th 2024 07:52:50 pm                                             #
# Modified   : Saturday September 7th 2024 08:47:51 pm                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import functools
from datetime import datetime
from typing import Awaitable, Callable, TypeVar

from appvocai.domain.monitor.errors import ErrorLog
from appvocai.infra.identity.passport import Passport
from appvocai.infra.repo.monitor.errors import ErrorLogRepo

F = TypeVar("F", bound=Callable[..., Awaitable])


# ------------------------------------------------------------------------------------------------ #
def log_error(repo: ErrorLogRepo) -> Callable[[F], F]:
    """
    Decorator for logging errors to the ErrorRepo via the add method,
    but throws an unlogged exception if no valid passport is found.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Attempt to find a passport in the arguments
            passport = None

            # Check positional arguments for a passport
            for arg in args:
                if isinstance(arg, Passport):
                    passport = arg
                    break

            # Check keyword arguments for a passport
            if not passport:
                for kwarg in kwargs.values():
                    if isinstance(kwarg, Passport):
                        passport = kwarg
                        break

            # If no valid passport, raise an unlogged exception
            if not passport:
                raise RuntimeError(
                    "Invalid passport: Passport is required but not found."
                )

            try:
                return await func(self, *args, **kwargs)
            except Exception as e:
                # If a passport is available, log the error
                error_log = ErrorLog(
                    project_id=passport.project_id,
                    job_id=passport.job_id,
                    task_id=passport.task_id,
                    data_type=passport.data_type,
                    operation_type=passport.operation_type,
                    error_type=type(e).__name__,
                    error_code=getattr(
                        e, "status", 500
                    ),  # Fallback to 500 if status code not available
                    error_description=str(e),
                    dt_error=datetime.now(),
                )

                # Log the error using the ErrorRepo's add method
                repo.add(error_log)

                # Optionally, you can also log the error using the logger
                args[0]._logger.exception(f"Error occurred: {e}")

                raise e  # Re-raise the exception after logging

        return wrapper

    return decorator
