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
# Modified   : Thursday August 1st 2024 01:37:52 am                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import logging
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from appstorestream.infra.web.throttle import AThrottleStage

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
    async def test_burnin_stage(self, burnin_stage, random_latencies, caplog):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} test_burnin_stage at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #

        metrics = await burnin_stage(random_latencies)
        assert metrics.current_rate is not None
        assert metrics.current_delay is not None
        assert metrics.current_stage == AThrottleStage.BURNIN
        assert metrics.current_mean_latency is not None
        assert metrics.current_std_latency is not None
        assert metrics.current_cv_latency is not None

        logger.info(f"Burnin Stage Metrics: {metrics}")
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
            f"\n\nStarted {self.__class__.__name__} test_exploration_stage at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #

        metrics = await exploration_stage(random_latencies)
        assert metrics.current_rate is not None
        assert metrics.current_delay is not None
        assert metrics.current_stage == AThrottleStage.EXPLORATION
        assert metrics.current_mean_latency is not None
        assert metrics.current_std_latency is not None
        assert metrics.current_cv_latency is not None

        logger.info(f"Exploration Stage Metrics: {metrics}")
        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)
        logger.info(
            f"\n\nCompleted {self.__class__.__name__} test_exploration_stage in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    @pytest.mark.asyncio
    async def test_exploitation_pid(self, exploitation_pid, random_latencies, caplog):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} test_exploitation_pid at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #

        metrics = await exploitation_pid(random_latencies)
        assert metrics.current_rate is not None
        assert metrics.current_delay is not None
        assert metrics.current_stage == AThrottleStage.EXPLOITATION_PID
        assert metrics.current_mean_latency is not None
        assert metrics.current_std_latency is not None
        assert metrics.current_cv_latency is not None

        logger.info(f"Exploitation PID Metrics: {metrics}")
        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)
        logger.info(
            f"\n\nCompleted {self.__class__.__name__} test_exploitation_pid in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    @pytest.mark.asyncio
    async def test_exploitation_pid_multivariate(
        self, exploitation_pid_multivariate, random_latencies, caplog
    ):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} test_exploitation_pid_multivariate at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #

        metrics = await exploitation_pid_multivariate(random_latencies)
        assert metrics.current_rate is not None
        assert metrics.current_delay is not None
        assert metrics.current_stage == AThrottleStage.EXPLOITATION_PID_MULTIVARIATE
        assert metrics.current_mean_latency is not None
        assert metrics.current_std_latency is not None
        assert metrics.current_cv_latency is not None

        logger.info(f"Exploitation PID Multivariate Metrics: {metrics}")
        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)
        logger.info(
            f"\n\nCompleted {self.__class__.__name__} test_exploitation_pid_multivariate in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    @pytest.mark.asyncio
    async def test_controller(self, controller, random_latencies, caplog):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} test_controller at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #

        for stage in controller.stages.values():
            metrics = await stage(random_latencies)
            assert metrics.current_rate is not None
            assert metrics.current_delay is not None
            assert metrics.current_stage in AThrottleStage
            assert metrics.current_mean_latency is not None
            assert metrics.current_std_latency is not None
            assert metrics.current_cv_latency is not None

            logger.info(f"Controller Stage Metrics: {metrics}")

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)
        logger.info(
            f"\n\nCompleted {self.__class__.__name__} test_controller in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
