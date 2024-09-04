#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/metrics/base.py                                               #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 09:04:54 pm                                               #
# Modified   : Tuesday September 3rd 2024 05:15:02 pm                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from appvocai.core.data import DataClass


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Metrics(DataClass):
    """
    Base class for capturing and computing task-related metrics.

    This class is designed to be extended by concrete metrics classes specific to different tasks.
    It provides basic functionality to track the start and end time of a task, calculate its duration,
    and compute additional metrics as needed.
    """

    start: Optional[datetime] = None  # timestamp when the task started.
    end: Optional[datetime] = None  # The timestamp when the task ended.
    duration: float = (
        0.0  # The duration of the task in seconds, computed as the difference between end and start times.
    )

    def pre(self) -> None:
        """
        Marks the start time of the task.

        This method should be called at the beginning of the task execution to record
        the current UTC time as the start time.
        """
        self.start = datetime.now(timezone.utc)

    def post(self) -> None:
        """
        Marks the end time of the task and computes its duration.

        This method should be called at the end of the task execution to record the current
        UTC time as the end time. It also computes the task duration by calculating the
        difference between the end and start times.
        """
        self.end = datetime.now(timezone.utc)
        if isinstance(self.start, datetime):
            self.duration = (self.end - self.start).total_seconds()

    @abstractmethod
    def compute(self, *args: Any, **kwargs: Any) -> None:
        """
        Computes additional metrics based on the provided arguments.

        This method is abstract and should be implemented by subclasses to perform specific
        metrics calculations required by the task.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        pass

    @abstractmethod
    def validate(self) -> None:
        """
        Validates the metrics data.

        This method is intended to be implemented by subclasses to perform specific validation
        checks on the metrics data. The validation process should include checks for any invalid
        or unexpected values (e.g., negative values where they shouldn't exist) and issue warnings
        or raise errors as appropriate.

        Subclasses should override this method to ensure that all metrics adhere to the expected
        constraints and are safe to use in subsequent calculations or updates.

        Raises:
            ValueError: Subclasses may raise this exception if the validation fails critically.
        """
