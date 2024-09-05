#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/operator/transform/metrics.py                                       #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 04:42:55 am                                                   #
# Modified   : Wednesday September 4th 2024 06:14:50 pm                                            #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import logging
from dataclasses import dataclass

from appvocai.infra.monitor.metrics import Metrics

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class MetricsTransformerAppData(Metrics):
    """"""

    records_in: int = 0  # Number of input records
    records_out: int = 0  # Number of output records
    throughput: float = 0.0  # Number of records processed per second of duration

    async def compute(self, records_in: int, records_out: int) -> None:
        """"""
        self.records_in = records_in
        self.records_out = records_out

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
        if self.records_in < 0:
            logger.warning(f"Negative value for records_in: {self.records_in}")
        if self.records_out < 0:
            logger.warning(f"Negative value for records_out: {self.records_out}")
        if self.throughput < 0:
            logger.warning(f"Negative value for throughput: {self.throughput}")
