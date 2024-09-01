#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/metrics/load.py                                                    #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 09:04:54 pm                                               #
# Modified   : Sunday September 1st 2024 03:43:33 am                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Extract Metrics Module"""
import logging
from dataclasses import dataclass

from appvocai.domain.metrics.base import Metrics

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
@dataclass
class MetricsLoad(Metrics):
    """
    Class for capturing and computing load-related metrics.

    This class tracks metrics related to the load phase of a task, including the number of records
    loaded, throughput, and errors encountered during the process.
    """

    records: int = 0  # Number of records loaded
    throughput: float = 0.0  # Number of records processed per second of duration
    errors: int = 0  # Number of errors encountered during the load process

    def compute(self, records: int, errors: int = 0) -> None:
        """
        Computes load-related metrics based on the provided number of records and errors.

        This method calculates the number of records loaded, throughput, and errors encountered
        during the load phase.

        Args:
            records (int): The number of records loaded.
            errors (int): The number of errors encountered during the load process. Defaults to 0.
        """
        self.records = records
        self.errors = errors
        self.throughput = self.records / self.duration if self.duration > 0 else 0.0

    def validate(self) -> None:
        """
        Validates the load metrics data.

        Checks for any invalid or unexpected values, such as negative values where they shouldn't exist,
        and issues warnings as appropriate.

        Raises:
            ValueError: May be raised if the validation identifies critical issues.
        """
        if self.records < 0:
            logger.warning(f"Negative value for records: {self.records}")
        if self.errors < 0:
            logger.warning(f"Negative value for errors: {self.errors}")
        if self.throughput < 0:
            logger.warning(f"Negative value for throughput: {self.throughput}")
