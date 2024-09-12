#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_domain/test_domain_appdata/test_appdata_request_gen.py                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday September 4th 2024 11:50:48 pm                                            #
# Modified   : Monday September 9th 2024 04:57:55 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import inspect
import logging
from datetime import datetime

import pytest

from acquire.domain.artifact.request.appdata import (
    AsyncRequestAppData,
    RequestAppData,
    RequestAppDataGen,
)

# ------------------------------------------------------------------------------------------------ #
# pylint: disable=missing-class-docstring, line-too-long
# mypy: ignore-errors
# ------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"
# ------------------------------------------------------------------------------------------------ #
CATEGORY_ID = 6018
MAX_REQUESTS = 4
BATCH_SIZE = 2
LIMIT = 10


@pytest.mark.gen
class TestAppDataRequestGen:  # pragma: no cover
    # ============================================================================================ #
    def test_appdata_request_gen(self, caplog) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        gen = RequestAppDataGen(
            task_passport=
            category_id=CATEGORY_ID,
            max_requests=MAX_REQUESTS,
            batch_size=BATCH_SIZE,
            limit=LIMIT,
        )
        n_requests = 0
        for arequest in gen:
            assert isinstance(arequest, AsyncRequestAppData)
            assert arequest.request_count == BATCH_SIZE
            for request in arequest.requests:
                assert isinstance(request, RequestAppData)
                n_requests += 1
                print(request)

        assert n_requests == MAX_REQUESTS

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
