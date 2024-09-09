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
# Modified   : Sunday September 8th 2024 07:59:41 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import functools
from datetime import datetime
from typing import Awaitable, Callable, TypeVar

from appvocai.application.orchestration.context import JobContext
from appvocai.domain.monitor.errors import ErrorLog
from appvocai.infra.repo.monitor.errors import ErrorLogRepo

F = TypeVar("F", bound=Callable[..., Awaitable])


# ------------------------------------------------------------------------------------------------ #
def log_error(repo: ErrorLogRepo) -> Callable[[F], F]:
    """
    Decorator for logging errors to the ErrorRepo via the add method,
    but throws an unlogged exception if no valid context is found.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Attempt to find a context in the arguments
            context = None

            # Check positional arguments for a context
            for arg in args:
                if isinstance(arg, JobContext):
                    context = arg
                    break

            # Check keyword arguments for a context
            if not context:
                for kwarg in kwargs.values():
                    if isinstance(kwarg, JobContext):
                        context = kwarg
                        break

            # If no valid context, raise an unlogged exception
            if not context:
                raise RuntimeError(
                    "Invalid context: JobContext is required but not found."
                )

            try:
                return await func(self, *args, **kwargs)
            except Exception as e:
                # If a context is available, log the error
                error_log = ErrorLog(
                    project_id=context.project_id,
                    job_id=context.job_id,
                    task_id=context.task_id,
                    data_type=context.data_type,
                    stage_type=context.stage_type,
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

        return wrapper

    return decorator
