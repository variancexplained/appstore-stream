#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_infra/test_web/test_async_request.py                                    #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday August 26th 2024 11:13:46 pm                                                 #
# Modified   : Tuesday August 27th 2024 03:49:55 pm                                                #
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

from appvocai.domain.request.appdata import RequestAppData
from appvocai.domain.request.review import RequestAppReview

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
END_IDX = LIMIT


@pytest.mark.asyncio
class TestRequestAppData:  # pragma: no cover
    # ============================================================================================ #
    @pytest.mark.skip(reason="working")
    @pytest.mark.asyncio1
    async def test_request_appdata(self, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #

        request = RequestAppData(genreId=CATEGORY, current_page=PAGE, limit=LIMIT)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                request.baseurl,
                headers=request.headers,
                proxy=request.proxy,
                params=request.params,
            ) as response:
                result = await response.json(content_type=None)
                assert len(result["results"]) == LIMIT
                assert isinstance(result["results"], list)
            logging.debug(f"\n\nAppData Response: \n{response}")
            logging.debug(f"\n\nAppData Response UUID: \n{response.headers.get('x-apple-request-uuid',None)}")
            logging.debug(f"\n\nAppData Response Server: \n{response.headers.get('Server','unknown-server')}")

            logging.debug(f"\n\nAppData Response Content-Type: \n{response.content_type}")
            logging.debug(f"\n\nAppData Response Encoding: \n{response.headers.get('Content-Encoding',None)}")
            logging.debug(f"\n\nAppData Response Strict Transport Security: \n{response.headers.get('strict-transport-security','max-age=0')}")
            logging.debug(f"\n\nAppData Response Content Length: \n{response.content_length}")
            logging.debug(f"\n\nAppData Response Cache Control: \n{response.headers.get('Cache-Control','no-cache')}")
            logging.debug(f"\n\nAppData Response Date: \n{response.headers.get('Date',None)}")
            logging.debug(f"\n\nAppData Response Connection: \n{response.connection}")
            logging.debug(f"\n\nAppData Response X-Cache: \n{response.headers.get('X-Cache',response.headers.get('X-Cache-Remote',None))}")
            logging.debug(f"\n\nAppData Content: \n{result}")
            assert response.status == 200
            assert response.content_length > 0

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    # @pytest.mark.skip(reason="working")
    @pytest.mark.asyncio2
    async def test_request_review(self, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #

        request = RequestAppReview(
            app_id=544007664, page=0, limit=LIMIT
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=request.baseurl,
                headers=request.headers,
                proxy=request.proxy,
            ) as response:
                result = await response.json()
                assert len(result["userReviewList"]) == END_IDX
            logging.debug(f"\n\nAppReview Response: \n{response}")
            logging.debug(f"\n\nAppData Content: \n{result}")

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
