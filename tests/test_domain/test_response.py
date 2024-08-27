#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_domain/test_response.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday August 27th 2024 05:06:05 pm                                                #
# Modified   : Tuesday August 27th 2024 06:44:01 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import asyncio
import inspect
import json
import logging
from datetime import datetime, timezone
from typing import Any

import aiohttp
import pandas as pd
import pytest

from appvocai.domain.request.appdata import RequestAppData
from appvocai.domain.request.review import RequestAppReview
from appvocai.domain.response.appdata import ResponseAppData
from appvocai.domain.response.review import ResponseAppReview

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
APP_ID = 544007664

@pytest.mark.asyncio
@pytest.mark.response
class TestResponse:  # pragma: no cover
    # ============================================================================================ #
    #@pytest.mark.skip(reason="working")

    async def test_response_appdata(self, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        request = RequestAppData(genreId=CATEGORY, page=PAGE, limit=LIMIT)
        request.date_time = datetime.now(timezone.utc)
        resp = ResponseAppData()
        resp.parse_request(request=request)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                request.baseurl,
                headers=request.headers,
                proxy=request.proxy,
                params=request.params,
            ) as response:
                await resp.parse_response(response=response)
                logging.debug(f"\n\nResponse UUID:\n{response.headers.get('x-apple-request-uuid')}")
                logging.debug(f"\n\nHeader:\n{response.headers}")


                resp.parse_response(response=response)
                logging.debug(resp)
                assert resp.id
                assert isinstance(resp.id,str)
                assert resp.request_uuid
                assert isinstance(resp.request_uuid,str)
                assert resp.request_type == "appdata"
                assert resp.method == "GET"
                assert "itunes" in resp.endpoint
                assert resp.start_index == PAGE * LIMIT
                assert resp.end_index == (PAGE + 1) * LIMIT
                assert not resp.server
                assert isinstance(resp.server_datetime,datetime)
                assert isinstance(resp.cache_control,str)
                assert resp.cache_control
                assert resp.connection
                assert resp.content_length
                assert resp.content_type
                assert resp.encoding
                assert resp.latency
                assert resp.n
                assert resp.response_datetime
                assert resp.status
                assert resp.strict_transport_security
                assert resp.vary
                assert resp.x_cache

                assert isinstance(resp.connection,str)
                assert isinstance(resp.content_length,str)
                assert isinstance(resp.content_type,str)
                assert isinstance(resp.encoding,str)
                assert isinstance(resp.latency,float)
                assert isinstance(resp.n,int)
                assert isinstance(resp.response_datetime,datetime)
                assert isinstance(resp.status,int)
                assert isinstance(resp.strict_transport_security,str)
                assert isinstance(resp.vary,str)
                assert isinstance(resp.x_cache,str)

                logging.debug(resp)


        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    #@pytest.mark.skip(reason="working")
    async def test_response_review(self, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        request = RequestAppReview(app_id=APP_ID, page=PAGE, limit=LIMIT)
        request.date_time = datetime.now(timezone.utc)
        resp = ResponseAppReview()
        resp.parse_request(request=request)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                request.baseurl,
                headers=request.headers,
                proxy=request.proxy,
                params=request.params,
            ) as response:
                await resp.parse_response(response=response)

                resp.parse_response(response=response)
        assert resp.id
        assert isinstance(resp.id,str)
        assert resp.request_uuid
        assert isinstance(resp.request_uuid,str)
        assert resp.request_type == "review"
        assert resp.method == "GET"
        assert "itunes" in resp.endpoint
        assert "woa" in resp.endpoint
        assert resp.start_index == PAGE * LIMIT
        assert resp.end_index == (PAGE + 1) * LIMIT
        assert resp.server
        assert isinstance(resp.server_datetime,datetime)
        assert isinstance(resp.cache_control,str)
        assert resp.cache_control
        assert resp.connection
        assert resp.content_length
        assert resp.content_type
        assert resp.encoding
        assert resp.latency
        assert resp.n
        assert resp.response_datetime
        assert resp.status
        assert resp.strict_transport_security
        assert resp.vary
        assert resp.x_cache

        assert isinstance(resp.connection,str)
        assert isinstance(resp.content_length,str)
        assert isinstance(resp.content_type,str)
        assert isinstance(resp.encoding,str)
        assert isinstance(resp.latency,float)
        assert isinstance(resp.n,int)
        assert isinstance(resp.response_datetime,datetime)
        assert isinstance(resp.status,int)
        assert isinstance(resp.strict_transport_security,str)
        assert isinstance(resp.vary,str)
        assert isinstance(resp.x_cache,str)

        logging.debug(resp)


        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

