#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_infra/test_web/test_session_profile.py                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday August 23rd 2024 08:03:21 am                                                 #
# Modified   : Tuesday August 27th 2024 06:26:13 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import inspect
import logging
import time
from collections import deque
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import pytest

from appvocai.infra.web.profile import (
    SessionHistory,
    SessionProfile,
    SessionStats,
)

# ------------------------------------------------------------------------------------------------ #
# pylint: disable=missing-class-docstring, line-too-long
# ------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"


@pytest.mark.profile
class TestSessionProfile:  # pragma: no cover
    # ============================================================================================ #
    def test_profile(self, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        profile = SessionProfile()
        profile.send()
        for i in range(10):
            profile.add_latency(latency=np.random.random())
            time.sleep(0.01)
        profile.recv()

        assert isinstance(profile.get_latencies(), deque)
        assert isinstance(profile.get_throughput(), tuple)

        logging.info(profile.get_latencies())
        logging.info(profile.get_throughput())

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        response_time = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {response_time} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)


@pytest.mark.history
class TestHistory:  # pragma: no cover
    # ============================================================================================ #
    def test_add_metrics(self, session_history: SessionHistory, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        assert session_history.requests == 100
        assert session_history.sessions == 10

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        response_time = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {response_time} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_get_requests(self, session_history: SessionHistory, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        assert session_history.get_requests() == 100
        assert session_history.get_sessions() == 10

        assert session_history.get_requests() == 100
        assert session_history.get_requests(time_window=2) < 100

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        response_time = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {response_time} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_latency_stats(self, session_history: SessionHistory, caplog: Any) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        latency = session_history.get_latency_stats()
        assert isinstance(latency, SessionStats)
        logging.info(latency)

        latency = session_history.get_latency_stats(time_window=3)
        assert isinstance(latency, SessionStats)
        logging.info(latency)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        response_time = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {response_time} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_throughput_stats(
        self, session_history: SessionHistory, caplog: Any
    ) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        throughput = session_history.get_throughput_stats()
        assert isinstance(throughput, SessionStats)
        logging.info(throughput)

        throughput = session_history.get_throughput_stats(time_window=2)
        assert isinstance(throughput, SessionStats)
        logging.info(throughput)
        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        response_time = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {response_time} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
