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
# Modified   : Friday August 23rd 2024 07:39:31 pm                                                 #
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

        baseline.next_stage = rate
        rate.next_stage = concurrency
        concurrency.next_stage = exploit
        exploit.next_stage = baseline

        adapter = container.session().adapter
        # Validate instantiation
        assert isinstance(adapter, Adapter)
        assert isinstance(adapter.stage, AdapterBaselineStage)
        # Run a few sessions
        for i in range(NUM_SESSIONS):
            adapter.adapt(history=session_history)
            assert isinstance(adapter.session_control, SessionControl)
            assert adapter.session_control.rate == 50
            assert adapter.session_control.delay == 1
            assert adapter.session_control.concurrency == 50

        # Validate Baseline Statistical Snapshot
        assert isinstance(adapter.snapshot, StatisticalSnapshot)
        assert isinstance(adapter.snapshot.latency_stats, SessionStats)
        assert isinstance(adapter.snapshot.throughput_stats, SessionStats)
        assert isinstance(adapter.snapshot.rate_stats, SessionStats)
        assert isinstance(adapter.snapshot.delay_stats, SessionStats)
        assert isinstance(adapter.snapshot.concurrency_stats, SessionStats)
        assert isinstance(adapter.snapshot.requests, int)
        assert isinstance(adapter.snapshot.sessions, int)
        assert adapter.snapshot.requests == 100
        assert adapter.snapshot.sessions == 10

        ## Check SessionStats
        assert isinstance(adapter.snapshot.latency_stats.min, float)
        assert isinstance(adapter.snapshot.latency_stats.max, float)
        assert isinstance(adapter.snapshot.latency_stats.median, float)
        assert isinstance(adapter.snapshot.latency_stats.average, float)
        assert isinstance(adapter.snapshot.latency_stats.std, float)
        assert isinstance(adapter.snapshot.latency_stats.cv, float)

        ## Latency
        assert adapter.snapshot.latency_stats.min > 0
        assert adapter.snapshot.latency_stats.max > 0
        assert adapter.snapshot.latency_stats.median > 0
        assert adapter.snapshot.latency_stats.std > 0
        assert adapter.snapshot.latency_stats.average > 0
        assert adapter.snapshot.latency_stats.cv > 0

        ## Throughput
        assert adapter.snapshot.throughput_stats.min > 0
        assert adapter.snapshot.throughput_stats.max > 0
        assert adapter.snapshot.throughput_stats.median > 0
        assert adapter.snapshot.throughput_stats.std > 0
        assert adapter.snapshot.throughput_stats.average > 0
        assert adapter.snapshot.throughput_stats.cv > 0

        ## Rate
        assert adapter.snapshot.rate_stats.min > 0
        assert adapter.snapshot.rate_stats.max > 0
        assert adapter.snapshot.rate_stats.median > 0
        assert adapter.snapshot.rate_stats.std > 0
        assert adapter.snapshot.rate_stats.average > 0
        assert adapter.snapshot.rate_stats.cv > 0

        # Delay
        assert adapter.snapshot.delay_stats.min > 0
        assert adapter.snapshot.delay_stats.max > 0
        assert adapter.snapshot.delay_stats.median > 0
        assert adapter.snapshot.delay_stats.std > 0
        assert adapter.snapshot.delay_stats.average > 0
        assert adapter.snapshot.delay_stats.cv > 0

        # Concurrency
        assert adapter.snapshot.concurrency_stats.min == 50
        assert adapter.snapshot.concurrency_stats.max == 50
        assert adapter.snapshot.concurrency_stats.median == 50
        assert adapter.snapshot.concurrency_stats.std == 0
        assert adapter.snapshot.concurrency_stats.average == 50
        assert adapter.snapshot.concurrency_stats.cv == 0

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
