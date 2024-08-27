#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_infra/test_web/test_async_request.py                                    #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday August 26th 2024 11:13:46 pm                                                 #
# Modified   : Tuesday August 27th 2024 01:40:46 am                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import asyncio
import inspect
import json
import logging
from datetime import datetime
from typing import Any

import aiohttp
import pandas as pd
import pytest

from appstorestream.domain.request.appdata import RequestAppData
from appstorestream.domain.request.review import RequestReview

# ------------------------------------------------------------------------------------------------ #
# pylint: disable=missing-class-docstring, line-too-long
# mypy: ignore-errors
# ------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"

CATEGORY = 6018
PAGE = 2
LIMIT = 10
OFFSET = 0
START_IDX = 0
END_IDX = 20


@pytest.mark.asyncio
@pytest.mark.request
class TestRequestAppData:  # pragma: no cover
    # ============================================================================================ #
    @pytest.mark.skip(reason="working")
    async def test_request_appdata(self, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #

        request = RequestAppData(genreId=CATEGORY, current_page=PAGE, limit=LIMIT)
        async with aiohttp.ClientSession() as session:
            async with session.get(request.baseurl, params=request.params) as response:
                result = await response.json(content_type=None)
                assert len(result["results"]) == LIMIT
                assert isinstance(result["results"], list)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    async def test_request_review(self, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #

        request = RequestReview(
            app_id=544007664, start_index=START_IDX, end_index=END_IDX
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=request.baseurl, headers=request.header
            ) as response:
                result = await response.json()
                assert len(result["userReviewList"]) == END_IDX

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
