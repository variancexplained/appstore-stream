#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_domain/test_requests.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday August 27th 2024 03:27:58 am                                                #
# Modified   : Tuesday August 27th 2024 10:23:58 am                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import inspect
import logging
from datetime import datetime
from typing import Any, Optional

import pandas as pd
import pytest

from appvocai.domain.request.appdata import (
    RequestAppData,
    RequestAppDataGen,
    RequestAsyncAppData,
)
from appvocai.domain.request.review import (
    RequestAppReview,
    RequestAppReviewGen,
    RequestAsyncAppReview,
)

# ------------------------------------------------------------------------------------------------ #
# pylint: disable=missing-class-docstring, line-too-long
# mypy: ignore-errors
# ------------------------------------------------------------------------------------------------ #
CATEGORY_ID = 6018
BATCH_SIZE = 10
MAX_REQUESTS = 5

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"


@pytest.mark.request
class TestRequest:  # pragma: no cover
    # ============================================================================================ #
    def test_appdata_request_gen(self, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        gen = RequestAppDataGen(
            category_id=CATEGORY_ID, batch_size=BATCH_SIZE, max_requests=MAX_REQUESTS
        )
        for i, asyncrequest in enumerate(gen):
            assert isinstance(asyncrequest, RequestAsyncAppData)
            assert len(asyncrequest.requests) == MAX_REQUESTS
            assert (
                asyncrequest.requests[0].params["offset"]
                == i * asyncrequest.requests[0].params["limit"]
            )
            assert asyncrequest.requests[0].params["genreId"] == CATEGORY_ID

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_review_request_gen(self, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        gen = RequestAppReviewGen(
            app_id=CATEGORY_ID, batch_size=BATCH_SIZE, max_requests=MAX_REQUESTS
        )
        for i, asyncrequest in enumerate(gen):
            assert isinstance(asyncrequest, RequestAsyncAppReview)
            assert len(asyncrequest.requests) == MAX_REQUESTS
            assert asyncrequest.requests[0].app_id == CATEGORY_ID

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
