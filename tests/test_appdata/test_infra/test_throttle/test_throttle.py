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
# Modified   : Friday August 2nd 2024 09:27:51 am                                                  #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import asyncio
import inspect
import logging
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from appstorestream.infra.web.throttle import AThrottleStatus

# ------------------------------------------------------------------------------------------------ #
# pylint: disable=missing-class-docstring, line-too-long
# ------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"


@pytest.mark.throttle
@pytest.mark.asyncio
class TestThrottleStages:  # pragma: no cover
    # ============================================================================================ #
    @pytest.mark.asyncio
    async def test_burnin_stage(
        self, burnin_stage, random_latencies, exploration_stage, caplog
    ):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} test_burnin_stage at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #

        for i in range(3):
            await burnin_stage(random_latencies)
            logger.debug(burnin_stage.metrics)
            assert burnin_stage.metrics.baseline_mean_latency == 0
            assert burnin_stage.metrics.baseline_std_latency == 0
            assert burnin_stage.metrics.baseline_cv_latency == 0
            assert burnin_stage.controller.state == AThrottleStatus.BURNIN

        # Wait for stage to expire.
        await asyncio.sleep(2)
        # Call it after stage expires. Updates statistics
        await burnin_stage(random_latencies)
        assert burnin_stage.metrics.baseline_mean_latency != 0
        assert burnin_stage.metrics.baseline_std_latency != 0
        assert burnin_stage.metrics.baseline_cv_latency != 0
        assert burnin_stage.metrics.current_rate == 50
        assert burnin_stage.controller.state == AThrottleStatus.EXPLORE

        logger.debug(burnin_stage.metrics)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)
        logger.info(
            f"\n\nCompleted {self.__class__.__name__} test_burnin_stage in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    async def test_exploration_stage(self, exploration_stage, random_latencies, caplog):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        rate = 50
        await exploration_stage(random_latencies)
        assert exploration_stage.metrics.current_rate != rate
        rate = exploration_stage.metrics.current_rate
        logger.debug(exploration_stage.metrics)

        # Rate shouldn't change as still in the observation period.
        await exploration_stage(random_latencies)
        assert exploration_stage.metrics.current_rate == rate
        logger.debug(exploration_stage.metrics)
        # Wait for stage to expire.
        await asyncio.sleep(3)
        # Rate should change since observation period expired.
        await exploration_stage(random_latencies)
        assert exploration_stage.metrics.current_rate != rate
        # save rate as it will be reduced in the next iteration, following the observation period.
        oldrate = exploration_stage.metrics.current_rate
        logger.debug(exploration_stage.metrics)

        # Wait for stage to expire.
        await asyncio.sleep(3)

        random_latencies2 = list(np.random.randint(10, 500, 10))
        assert (isinstance(latency, (int, float)) for latency in random_latencies2)
        # Rate should reduce since observation period expired, and not stable.
        await exploration_stage(random_latencies2)
        assert exploration_stage.metrics.current_rate != rate
        assert (
            exploration_stage.metrics.current_rate == oldrate - 10
        )  # cooldown factor is 10
        logger.debug(exploration_stage.metrics)
        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
