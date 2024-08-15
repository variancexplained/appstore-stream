#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_appdata/test_infra/test_throttle/test_throttle.py                       #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday August 1st 2024 01:22:50 am                                                #
# Modified   : Thursday August 15th 2024 03:56:41 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import asyncio
import inspect
import logging
import time
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from appstorestream.infra.web.throttle import (
    AThrottle,
    AThrottleHistory,
    AThrottleStatus,
)

# ------------------------------------------------------------------------------------------------ #
# pylint: disable=missing-class-docstring, line-too-long
# ------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
matplotlib.pyplot.set_loglevel(level="warning")
# get the the logger with the name 'PIL'
pil_logger = logging.getLogger("PIL")
# override the logger logging level to INFO
pil_logger.setLevel(logging.INFO)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"


@pytest.mark.throttle
@pytest.mark.asyncio
class TestThrottleStages:  # pragma: no cover
    # ============================================================================================ #
    @pytest.mark.asyncio
    async def test_athrottle(self, container, random_latencies, caplog):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} test_burnin_stage at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        logger.debug("\n\nTestiing Burnin Stage")
        athrottle = container.web.athrottle()
        previous_rate = athrottle.rate
        previous_rate_changes = 0
        for i in range(20):
            await athrottle.throttle(random_latencies)
            logger.debug(athrottle)
            if athrottle.current_stage == AThrottleStatus.BURNIN.value:
                assert athrottle.rate == previous_rate
                assert athrottle.rate_changes == 0
            elif athrottle.current_stage == AThrottleStatus.EXPLORE.value:
                # Rate should increase monotonically because the site is stable.
                assert athrottle.rate == min(
                    previous_rate + athrottle.exploration_heatup_step_size,
                    athrottle.max_rate,
                )
                assert athrottle.rate_changes == previous_rate_changes + 1
                assert athrottle.rate_increases == athrottle.rate_changes
                previous_rate = athrottle.rate
                previous_rate_changes += 1
            else:
                assert athrottle.rate == previous_rate

        for i in range(1, 11):
            # Integrate instability
            random_unstable_latencies = list(np.random.randint(i, i + 10, 10))
            await athrottle.throttle(random_unstable_latencies)
            logger.debug(athrottle)
            if athrottle.current_stage == AThrottleStatus.EXPLORE:
                assert athrottle.rate < previous_rate
            if athrottle.current_stage == AThrottleStatus.EXPLOIT:
                assert athrottle.rate < previous_rate
            elif athrottle.current_stage == AThrottleStatus.BURNIN:
                assert athrottle.rate == previous_rate

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
