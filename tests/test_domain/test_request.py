#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_domain/test_request.py                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday August 27th 2024 04:07:35 pm                                                #
# Modified   : Tuesday August 27th 2024 05:03:24 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import inspect
import logging
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import pytest

from appvocai.domain.request.appdata import RequestAppDataGen
from appvocai.domain.request.review import RequestAppReviewGen

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
CATEGORY=6018
BATCH_SIZE = 2
LIMIT = 2
PAGES = 2
APP_ID = 544007664
@pytest.mark.gen
class TestRequestGen:  # pragma: no cover
    # ============================================================================================ #
    def test_appdata_request_gen(self, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        gen = RequestAppDataGen(category_id=CATEGORY,batch_size=BATCH_SIZE, start_page=0, limit=LIMIT, max_requests=20)
        for i, asyncrequest in enumerate(gen):
            for j, request in enumerate(asyncrequest.requests):
                request.date_time = datetime.now(timezone.utc)
                logging.debug(f"Page: {request.page}  Start: {request.start_index}   End: {request.end_index}  {request.baseurl}")
                logging.debug(request)
                logging.debug(request.headers)
                assert isinstance(request.date_time, datetime)
                assert request.request_type == 'appdata'
                assert isinstance(request.baseurl,str)
                assert isinstance(request.id,str)



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
        gen = RequestAppReviewGen(app_id=APP_ID, max_requests=20, batch_size=2, start_page=0, limit=2)
        for i, asyncrequest in enumerate(gen):
            for j, request in enumerate(asyncrequest.requests):
                request.date_time = datetime.now(timezone.utc)
                logging.debug(f"Page: {request.page}  Start: {request.start_index}   End: {request.end_index}  {request.baseurl}")
                logging.debug(request)
                logging.debug(request.headers)
                assert isinstance(request.date_time, datetime)
                assert request.request_type == 'review'
                assert isinstance(request.baseurl,str)
                assert isinstance(request.id,str)


        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
