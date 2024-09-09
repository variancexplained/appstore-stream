#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_extract/test_extract_appdata.py                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday September 7th 2024 09:22:36 pm                                             #
# Modified   : Sunday September 8th 2024 12:23:35 am                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import inspect
import logging
from datetime import datetime

import pytest

from appvocai.application.orchestration.job import Context
from appvocai.core.enum import Category, DataType, StageType
from appvocai.domain.artifact.request.base import AsyncRequest, Request

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
MAX_REQUESTS = 5
BATCH_SIZE = 5
START_PAGE = 10
LIMIT = 10

context = (
    Context(
        job_id="20240912-9",
        data_type=DataType.AppData,
        category=Category.PRODUCTIVITY,
        stage=StageType.EXTRACT,
    ),
)
# ------------------------------------------------------------------------------------------------ #


@pytest.mark.extract
class TestExtractAppData:  # pragma: no cover
    # ============================================================================================ #
    @pytest.mark.parametrize(
        "rgen_appdata",
        {
            "context": context,
            "max_requests": MAX_REQUESTS,
            "batch_size": BATCH_SIZE,
            "start_page": START_PAGE,
            "limit": LIMIT,
        },
        indirect=True,
    )
    def test_request_gen(self, rgen_appdata, caplog) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        assert isinstance(rgen_appdata.context, Context)
        assert rgen_appdata.max_requests == MAX_REQUESTS
        assert rgen_appdata.batchsize == BATCH_SIZE

        async_request = next(rgen_appdata)
        assert isinstance(async_request, AsyncRequest)
        assert async_request.request_count == 5

        for request in async_request.requests:
            assert isinstance(request, Request)
            logger.info(request)
        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
