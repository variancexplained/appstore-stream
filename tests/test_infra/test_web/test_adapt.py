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
# Modified   : Saturday August 24th 2024 08:52:06 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import inspect
import logging
import time
from datetime import datetime
from typing import Any, Optional

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
)

# ------------------------------------------------------------------------------------------------ #
# pylint: disable=missing-class-docstring, line-too-long
# mypy: ignore-errors
# ------------------------------------------------------------------------------------------------ #
NUM_SESSIONS = 5
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"


# ------------------------------------------------------------------------------------------------ #
class MockSessionHistory:
    def __init__(self) -> None:
        self._factor = 0.1
        self._calls = 0

    def get_latency_stats(self, time_window: Optional[int] = None) -> SessionStats:
        self._calls += 1
        logging.info(f"MockSessionHistory Call #{self._calls}")
        factor = -1
        if self._calls % 10 >= 5:
            factor = 1
        return SessionStats(
            min=0.06,
            max=0.99,
            median=0.45,
            average=0.46 + (0.46 * self._factor * self._calls * factor),
            std=0.270151472662687,
            cv=0.5831 + (0.58 * self._factor * self._calls * factor),
        )


@pytest.mark.adapt
@pytest.mark.adaptbaseline
class TestAdapt:  # pragma: no cover
    # ============================================================================================ #
    def test_baseline(
        self,
        container: AppStoreStreamContainer,
        monkeypatch,
        caplog: Any,
    ) -> None:  # type: ignore[no-untyped-def]
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

        def mock_history() -> MockSessionHistory:
            return MockSessionHistory()

        monkeypatch.setattr(SessionHistory, "get_latency_stats", mock_history)
        session_history = SessionHistory()

        # Validate instantiation
        assert isinstance(adapter, Adapter)
        assert isinstance(adapter.stage, AdapterBaselineStage)
        # Run a few sessions
        for i in range(NUM_SESSIONS):
            adapter.adapt_requests(history=session_history)
            assert isinstance(adapter.session_control, SessionControl)
            assert 45 <= round(adapter.session_control.rate, 0) <= 55
            assert round(adapter.session_control.delay, 0) == 1
            assert round(adapter.session_control.concurrency, 0) == 50

        # Check transition
        time.sleep(2)
        adapter.adapt_requests(history=session_history)
        assert isinstance(adapter.stage, AdapterRateExploreStage)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    @pytest.mark.adaptrate
    def test_rate_explorer(self, monkeypatch, adapter: Adapter, mock_history, caplog: Any) -> None:  # type: ignore[no-untyped-def]
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)

        # ---------------------------------------------------------------------------------------- #
        caplog.set_level(logging.DEBUG)

        monkeypatch.setattr(SessionHistory, "get_latency_stats", mock_history)
        history = SessionHistory()
        rates = []
        for i in range(10):
            adapter.adapt_requests(history=history)
            rate = adapter.session_control.rate
            rates.append(rate)
            assert round(rate, 0) >= 50
            if i % 2 == 0:
                time.sleep(1)

        logging.info(f"\nThe Rates should increase, then decrease.\n{rates}")

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    @pytest.mark.adaptc
    def test_concurrency_explorer(self, monkeypatch, adapter: Adapter, mock_history, caplog: Any) -> None:  # type: ignore[no-untyped-def]
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)

        # ---------------------------------------------------------------------------------------- #
        caplog.set_level(logging.DEBUG)

        monkeypatch.setattr(SessionHistory, "get_latency_stats", mock_history)
        history = SessionHistory()
        concurrencies = []
        for i in range(20):
            adapter.adapt_requests(history=history)
            concurrency = adapter.session_control.concurrency
            concurrencies.append(concurrency)
            if i % 2 == 0:
                time.sleep(1)

        logging.info(
            f"\n\nThe Concurrencies should slowly rise then back off..\n{concurrencies}"
        )

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    @pytest.mark.adapte
    def test_concurrency_explorer(self, monkeypatch, adapter: Adapter, mock_history, caplog: Any) -> None:  # type: ignore[no-untyped-def]
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)

        # ---------------------------------------------------------------------------------------- #
        caplog.set_level(logging.DEBUG)

        monkeypatch.setattr(SessionHistory, "get_latency_stats", mock_history)
        history = SessionHistory()
        rates = []
        for i in range(20):
            adapter.adapt_requests(history=history)
            rate = adapter.session_control.rate
            rates.append(rate)
            if i % 2 == 0:
                time.sleep(1)

        logging.info(f"\n\nThe Rates should slowly rise than backoff.\n{rates}")

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
