#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_infra/test_web/test_adapt.py                                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday August 23rd 2024 03:02:47 pm                                                 #
# Modified   : Saturday August 24th 2024 10:25:25 am                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import inspect
import logging
import time
from datetime import datetime
from typing import Any

import pytest
from dependency_injector.containers import Container

from appstorestream.container import AppStoreStreamContainer
from appstorestream.infra.web.adapter import (
    Adapter,
    AdapterBaselineStage,
    AdapterConcurrencyExploreStage,
    AdapterExploitStage,
    AdapterRateExploreStage,
)
from appstorestream.infra.web.profile import (
    SessionControl,
    SessionHistory,
    SessionStats,
    StatisticalSnapshot,
)

# ------------------------------------------------------------------------------------------------ #
# pylint: disable=missing-class-docstring, line-too-long
# ------------------------------------------------------------------------------------------------ #
NUM_SESSIONS = 5
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"


@pytest.mark.adapt
class TestAdapter:  # pragma: no cover
    # ============================================================================================ #
    def test_baseline(
        self,
        session_history: SessionHistory,
        container: AppStoreStreamContainer,
        caplog: Any,
    ) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        baseline = container.session.baseline()
        rate = container.session.rate()
        concurrency = container.session.concurrency()
        exploit = container.session.exploit()
        adapter = container.session.adapter()

        baseline.next_stage = rate
        rate.next_stage = concurrency
        concurrency.next_stage = exploit
        exploit.next_stage = baseline

        # Validate instantiation
        assert isinstance(adapter, Adapter)
        assert isinstance(adapter.stage, AdapterBaselineStage)
        # Run a few sessions
        for i in range(NUM_SESSIONS):
            adapter.adapt(history=session_history)
            assert isinstance(adapter.session_control, SessionControl)
            assert round(adapter.session_control.rate, 0) == 50
            assert round(adapter.session_control.delay, 0) == 1
            assert round(adapter.session_control.concurrency, 0) == 50

        # Check transition
        time.sleep(2)
        adapter.adapt(history=session_history)
        assert isinstance(adapter.stage, AdapterRateExploreStage)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
