#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_infra/test_web/test_appdata_asession.py                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday July 29th 2024 01:09:08 pm                                                   #
# Modified   : Sunday August 25th 2024 12:11:47 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import inspect
import logging
from datetime import datetime

import aiohttp
import pandas as pd
import pytest

from appstorestream.domain.appdata.request import AppDataRequestGen

CATEGORY = 6018
MAX_REQUESTS = 10
BATCH_SIZE = 2
START_PAGE = 0
RESULTS_PER_PAGE = 200
# ------------------------------------------------------------------------------------------------ #
# pylint: disable=missing-class-docstring, line-too-long
# ------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"


@pytest.mark.appdata
@pytest.mark.asession
@pytest.mark.asyncio
class TestAppDataAsession:  # pragma: no cover
    # ============================================================================================ #
    async def test_appdata_asession(self, container, caplog):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        session = container.web.asession_appdata()
        rgen = AppDataRequestGen(
            category_id=CATEGORY,
            max_requests=MAX_REQUESTS,
            batch_size=BATCH_SIZE,
            start_page=START_PAGE,
        )

        for request in iter(rgen):
            assert isinstance(request.param_list, list)
            assert isinstance(request.baseurl, str)
            assert len(request.param_list) == 2
            response = await session.get(request=request)
            response.process_response()
            logger.debug(str(response.metrics))
            assert response.metrics.request_count == BATCH_SIZE
            assert response.metrics.response_count == BATCH_SIZE
            assert response.metrics.record_count <= BATCH_SIZE * RESULTS_PER_PAGE
            assert len(response.content) == response.metrics.record_count
            logging.debug(response.content.head())

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        response_time = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {response_time} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
