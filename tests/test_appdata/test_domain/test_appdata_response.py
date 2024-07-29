#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_appdata/test_domain/test_appdata_response.py                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday July 29th 2024 06:56:32 am                                                   #
# Modified   : Monday July 29th 2024 02:52:22 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import inspect
import logging
import time
from datetime import datetime

import pandas as pd
import pytest

from appstorestream.domain.appdata.response import AppDataAsyncResponse

# ------------------------------------------------------------------------------------------------ #
# pylint: disable=missing-class-docstring, line-too-long
# ------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"


@pytest.mark.appdata
@pytest.mark.response
class TestAppDataResponse:  # pragma: no cover
    # ============================================================================================ #
    def test_request_response(self, appdata_json, caplog):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        response = AppDataAsyncResponse()
        response.send()
        time.sleep(2)
        response.recv(results=appdata_json)
        assert isinstance(response.content, list)
        assert isinstance(response.get_content(), pd.DataFrame)
        assert len(response.content) == 200
        assert isinstance(response.time_sent, datetime)
        assert isinstance(response.time_recv, datetime)
        assert response.request_count == 0
        assert response.response_count == 200
        assert response.record_count > 200
        assert response.request_throughput == 0
        assert response.response_throughput > 0
        assert response.record_throughput > response.response_throughput
        assert response.total_errors == 0
        assert response.total_error_rate == 0
        assert response.ok

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
