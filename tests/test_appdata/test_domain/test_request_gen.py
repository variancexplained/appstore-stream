#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_appdata/test_domain/test_request_gen.py                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday July 29th 2024 12:32:14 pm                                                   #
# Modified   : Monday July 29th 2024 02:52:38 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import inspect
import logging
from datetime import datetime

import pandas as pd
import pytest

from appstorestream.domain.appdata.request import AppDataAsyncRequestGen

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
@pytest.mark.rgen
class TestAppDataRequestGen:  # pragma: no cover
    # ============================================================================================ #
    def test_request_gen(self, caplog):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        rgen = AppDataAsyncRequestGen(
            category_id=CATEGORY,
            max_requests=MAX_REQUESTS,
            batch_size=BATCH_SIZE,
            start_page=START_PAGE,
        )
        assert rgen.bookmark == START_PAGE
        assert rgen.batchsize == BATCH_SIZE
        assert rgen.max_requests == MAX_REQUESTS

        requests = iter(rgen)

        page = START_PAGE
        batch = 0
        for request in requests:
            assert len(request.param_list) == BATCH_SIZE
            assert isinstance(request.param_list, list)
            batch += 1
            logger.debug(f"\n\nGenerating Batch: {batch}")
            for param in request.param_list:
                logger.debug(f"Printing Page: {page}")
                assert param["offset"] == page * RESULTS_PER_PAGE
                assert "media" in param.keys()
                assert "explicit" in param.keys()
                assert "country" in param.keys()
                assert "term" in param.keys()
                assert "genreId" in param.keys()
                page += 1
                logger.debug(param)

        assert requests.bookmark == 10
        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
