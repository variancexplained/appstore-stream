#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/metrics/transform.py                                               #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday August 31st 2024 09:04:54 pm                                               #
# Modified   : Sunday September 1st 2024 03:37:36 am                                               #
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
class MetricsTransform(Metrics):
    """
    Class for capturing and computing transform-related metrics.

    This class tracks metrics related to the transformation phase of a task, including the number of records
    processed (input and output), throughput, and errors.
    """

    records_in: int = 0  # Number of input records
    records_out: int = 0  # Number of output records
    throughput: float = 0.0  # Number of records processed per second of duration
    errors: int = 0  # Number of errors encountered in the transformation

    def compute(self, records_in: int, records_out: int, errors: int = 0) -> None:
        """
        Computes transform-related metrics based on the provided input and output records.

        This method calculates the number of records processed, throughput, and errors encountered
        during the transformation phase.

        Args:
            records_in (int): The number of input records.
            records_out (int): The number of output records.
            errors (int): The number of errors encountered during the transformation. Defaults to 0.
        """
        self.records_in = records_in
        self.records_out = records_out
        self.errors = errors
        self.throughput = self.records_out / self.duration if self.duration > 0 else 0.0

    def validate(self) -> None:
        """
        Validates the transform metrics data.

        Checks for any invalid or unexpected values, such as negative values where they shouldn't exist,
        and issues warnings as appropriate.

        Raises:
            ValueError: May be raised if the validation identifies critical issues.
        """
        if self.records_in < 0:
            logger.warning(f"Negative value for records_in: {self.records_in}")
        if self.records_out < 0:
            logger.warning(f"Negative value for records_out: {self.records_out}")
        if self.errors < 0:
            logger.warning(f"Negative value for errors: {self.errors}")
        if self.throughput < 0:
            logger.warning(f"Negative value for throughput: {self.throughput}")
