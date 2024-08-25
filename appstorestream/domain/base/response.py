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
# Modified   : Sunday August 25th 2024 01:03:39 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Application Layer Base Module"""
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union

import pandas as pd

from appstorestream.infra.web.profile import SessionProfile


# ------------------------------------------------------------------------------------------------ #
class AsyncResponse(ABC):

    def __init__(
        self, results: list[Dict[str, Union[str, int, float]]], profile: SessionProfile
    ) -> None:
        self._results: List[Dict[str, Union[str, int, float]]] = results
        self._content: List[Dict[str, Union[str, int, float]]] = []
        self._finalized: bool = False
        self._profile: SessionProfile = profile
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def ok(self) -> bool:
        return len(self._content) > 0

    @property
    def content(self) -> pd.DataFrame:
        df = pd.DataFrame()
        if not self._finalized:
            self._not_finalized()
        else:
            df = pd.DataFrame(self._content)
        return df

    @property
    def profile(self) -> SessionProfile:
        return self._profile

    def process_response(self) -> None:
        """Returns the content from the AsyncRequest as a pandas dictionary"""
        self.parse_results()
        self._finalized = True

    @abstractmethod
    def parse_results(self) -> None:
        """Parse the results"""

    def _not_finalized(self) -> None:
        self._logger.warning(
            "The response has not been finalized. Run process_response prior to accessing response content and metrics."
        )
