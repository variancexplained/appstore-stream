#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/domain/base/response.py                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 26th 2024 03:50:26 am                                                   #
# Modified   : Friday August 16th 2024 11:33:25 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Application Layer Base Module"""
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import pandas as pd

from appstorestream.application.metrics.extract import ExtractMetrics


# ------------------------------------------------------------------------------------------------ #
class AsyncResponse(ABC):
    def __init__(self, results: list, metrics: ExtractMetrics) -> None:
        self._results = results
        self._metrics = metrics
        self._content = []
        self._finalized = False
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def ok(self) -> bool:
        return len(self._content) > 0

    @property
    def metrics(self) -> ExtractMetrics:
        if not self._finalized:
            self._not_finalized()
        else:
            return self._metrics

    @property
    def content(self) -> pd.DataFrame:
        if not self._finalized:
            self._not_finalized()
        else:
            return pd.DataFrame(self._content)

    def process_response(self) -> pd.DataFrame:
        """Returns the content from the AsyncRequest as a pandas dictionary"""
        self.parse_results(results=self._results)
        self._metrics.finalize()
        self._finalized = True

    @abstractmethod
    def parse_results(self, results: list) -> None:
        """Parse the results"""

    def _not_finalized(self) -> None:
        self._logger.warning(
            "The response has not been finalized. Run process_response prior to accessing response content and metrics."
        )
