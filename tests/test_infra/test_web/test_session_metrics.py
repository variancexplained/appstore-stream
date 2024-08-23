#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_infra/test_web/test_session_metrics.py                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 21st 2024 08:36:35 am                                              #
# Modified   : Friday August 23rd 2024 05:51:55 am                                                 #
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
import pytest

from appstorestream.infra.web.profile import (
    SessionMetrics,
    SessionMetricsCollector,
    SessionStatistics,
)

# ------------------------------------------------------------------------------------------------ #
# pylint: disable=missing-class-docstring, line-too-long
# ------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"
# ------------------------------------------------------------------------------------------------ #
NUM_REQUESTS = 5
NUM_SESSIONS = 2
MAX_HISTORY = 1  # 1 seconds
LATENCY_AVE = 2
LATENCY_CV = 0.707107
THROUGHPUT_AVE = 0.5
THROUGHPUT_MIN = 1
THROUGHPUT_MAX = 10


# ------------------------------------------------------------------------------------------------ #
class MockCollector:

    @staticmethod
    def get_latencies() -> deque:
        latencies = deque()
        for i in range(NUM_REQUESTS):
            latencies.append((time.time(), i))
        return latencies

    @staticmethod
    def get_throughput() -> tuple:
        return (time.time(), np.random.randint(THROUGHPUT_MIN, THROUGHPUT_MAX))


@pytest.mark.metrics
@pytest.mark.session_metrics
class TestSessionMetrics:  # pragma: no cover
    # ============================================================================================ #
    def test_metrics_collector(self, caplog: Any):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        collector = SessionMetricsCollector()

        collector.send()
        for _ in range(NUM_REQUESTS):
            latency = np.random.randn()
            collector.add_latency(latency=latency)
            time.sleep(0.01)
        collector.recv()

        assert isinstance(collector.get_latencies(), deque)
        assert isinstance(collector.get_throughput(), tuple)

        logger.info(collector.get_latencies())
        logger.info(collector.get_throughput())

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_latency(self, monkeypatch, caplog):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)

        # ---------------------------------------------------------------------------------------- #
        def mock_get_latencies(*args, **kwargs):
            return MockCollector().get_latencies()

        def mock_get_throughput(*args, **kwargs):
            return MockCollector().get_throughput()

        monkeypatch.setattr(
            SessionMetricsCollector, "get_latencies", mock_get_latencies
        )
        monkeypatch.setattr(
            SessionMetricsCollector, "get_throughput", mock_get_throughput
        )
        collector = SessionMetricsCollector()
        metrics = SessionMetrics()

        for i in range(NUM_SESSIONS):
            metrics.update_metrics(collector=collector)
        stats = metrics.compute_latency_stats()
        assert stats.average == LATENCY_AVE
        assert round(stats.cv, 3) == round(LATENCY_CV, 3)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_throughput(self, monkeypatch, caplog):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)

        # ---------------------------------------------------------------------------------------- #
        def mock_get_latencies(*args, **kwargs):
            return MockCollector().get_latencies()

        def mock_get_throughput(*args, **kwargs):
            return MockCollector().get_throughput()

        monkeypatch.setattr(
            SessionMetricsCollector, "get_latencies", mock_get_latencies
        )
        monkeypatch.setattr(
            SessionMetricsCollector, "get_throughput", mock_get_throughput
        )
        collector = SessionMetricsCollector()
        metrics = SessionMetrics()

        for i in range(NUM_SESSIONS):
            metrics.update_metrics(collector=collector)
        stats = metrics.compute_throughput_stats()
        assert stats.average <= THROUGHPUT_MAX
        assert stats.average >= THROUGHPUT_MIN
        assert stats.cv >= 0
        assert stats.cv <= 1

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_pruning(self, monkeypatch, caplog):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)

        # ---------------------------------------------------------------------------------------- #
        def mock_get_latencies(*args, **kwargs):
            return MockCollector().get_latencies()

        def mock_get_throughput(*args, **kwargs):
            return MockCollector().get_throughput()

        monkeypatch.setattr(
            SessionMetricsCollector, "get_latencies", mock_get_latencies
        )
        monkeypatch.setattr(
            SessionMetricsCollector, "get_throughput", mock_get_throughput
        )
        collector = SessionMetricsCollector()
        metrics = SessionMetrics(max_history=MAX_HISTORY)

        # Maintaining only 1 second of results.
        for i in range(NUM_SESSIONS):
            metrics.update_metrics(collector=collector)
        assert metrics.requests == NUM_SESSIONS * NUM_REQUESTS
        assert metrics.sessions == NUM_SESSIONS

        time.sleep(1)

        # Adding more metrics should not increase the number of requests and sessions
        for i in range(NUM_SESSIONS):
            metrics.update_metrics(collector=collector)
        assert metrics.requests == NUM_SESSIONS * NUM_REQUESTS
        assert metrics.sessions == NUM_SESSIONS

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
