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
# Modified   : Wednesday August 21st 2024 08:46:05 am                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import inspect
import logging
import time
from collections import deque
from datetime import datetime

import numpy as np
import pytest

from appstorestream.infra.web.metrics import (
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


@pytest.mark.metrics
@pytest.mark.session_metrics
class TestSessionMetrics:  # pragma: no cover
    # ============================================================================================ #
    def test_metrics_collector(self, caplog):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        collector = SessionMetricsCollector()

        collector.send()
        for _ in range(5):
            latency = np.random.randn()
            collector.add_latency(latency=latency)
            time.sleep(0.01)
        collector.recv()

        assert isinstance(collector.get_latencies(), deque)
        assert isinstance(collector.get_throughput(), deque)

        logger.info(collector.get_latencies())
        logger.info(collector.get_throughput())

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
