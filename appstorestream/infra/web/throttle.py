#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/web/throttle.py                                               #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 04:44:47 am                                                   #
# Modified   : Sunday August 4th 2024 11:44:07 pm                                                  #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Autothrottle Module"""
from __future__ import annotations

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import List

import numpy as np
from scipy.stats import ttest_1samp

from appstorestream.core.data import DataClass


# ------------------------------------------------------------------------------------------------ #
class AThrottleStatus(Enum):
    BURNIN = 0
    EXPLORE = 1
    EXPLOIT = 2


# ------------------------------------------------------------------------------------------------ #
@dataclass
class AThrottleHistory:
    """
    A class to store and compute statistics for request latencies.

    Attributes:
        latency (deque): A deque to store latencies with a maximum length of 300000.
        latency_mean (deque): A deque to store the mean latencies with a maximum length of 30000.
        latency_std (deque): A deque to store the standard deviations of latencies with a maximum length of 30000.
        latency_cv (deque): A deque to store the coefficients of variation of latencies with a maximum length of 30000.
    """

    latency: deque = field(default_factory=lambda: deque(maxlen=300000))
    latency_mean: deque = field(default_factory=lambda: deque(maxlen=30000))
    latency_std: deque = field(default_factory=lambda: deque(maxlen=30000))
    latency_cv: deque = field(default_factory=lambda: deque(maxlen=30000))

    def add_latency(self, latencies: List[float]) -> None:
        """
        Add a list of latencies to the history.

        Args:
            latencies (List[float]): A list of latency values to add.
        """
        self.latency.extend(latencies)

    def compute_stats(self) -> None:
        """
        Compute and update the mean, standard deviation, and coefficient of variation for the stored latencies.

        If there are no latencies stored, the method does nothing.
        """
        if len(self.latency) > 0:
            mean = np.mean(self.latency)
            std = np.std(self.latency)
            cv = std / mean if mean != 0 else 0

            self.latency_mean.append(mean)
            self.latency_std.append(std)
            self.latency_cv.append(cv)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class AThrottle(DataClass):
    """
    A class to manage request throttling based on latency statistics, with different stages for burn-in, exploration, and exploitation.

    Attributes:
        athrottle_history (AThrottleHistory): An object to store and compute latency statistics.
        burnin_length (int): Length of the burn-in stage in seconds.
        explore_length (int): Length of the exploration stage in seconds.
        exploit_length (int): Length of the exploitation stage in seconds.
        concurrency (int): Number of requests per session.
        min_rate (float): Minimum requests per second.
        max_rate (float): Maximum requests per second.
        rate (float): Starting and current rate of requests per second.
        temperature (float): Controls the amount of random normal variation in the delay.
        exploration_heatup_step_size (int): Requests per second increase during exploration.
        exploration_cooldown_step_size (int): Requests per second decrease during exploration.
        threshold (float): The proportion change that stipulates a significant change.
        k (float): The proportion of change in latency to propagate to rate change.
        delay (float): The current delay in seconds.
        min_delay (float): Computed minimum delay from max rate.
        max_delay (float): Computed maximum delay from min rate.
        start_time (float): Start time for the current stage.
        current_stage (AThrottleStatus): The current stage of throttling.
        latency_mean (float): Current mean latency.
        latency_std (float): Current standard deviation of latency.
        latency_cv (float): Current coefficient of variation of latency.
        sessions (int): Number of sessions processed.
        requests (int): Number of requests processed.
        rate_changes (int): Number of rate changes.
        rate_increases (int): Number of rate increases.
        rate_decreases (int): Number of rate decreases.
    """

    athrottle_history: AThrottleHistory
    burnin_length: int = 300
    explore_length: int = 300
    exploit_length: int = 600
    concurrency: int = 100
    min_rate: float = 50.0
    max_rate: float = 1000.0
    rate: float = 50
    temperature: float = 0.5
    exploration_heatup_step_size: int = 10
    exploration_cooldown_step_size: int = -5
    threshold: float = 0.2
    k: float = 0.5
    delay: float = 2
    min_delay: float = field(init=False)
    max_delay: float = field(init=False)
    start_time: float = field(default_factory=time.time)
    current_stage: AThrottleStatus = field(default=AThrottleStatus.BURNIN)
    latency_mean: float = 0.0
    latency_std: float = 0.0
    latency_cv: float = 0.0
    sessions: int = 0
    requests: int = 0
    rate_changes: int = 0
    rate_increases: int = 0
    rate_decreases: int = 0

    def __post_init__(self):
        """
        Post-initialization to compute min and max delays based on min and max rates.
        """
        self.min_delay = (
            1 / self.max_rate * self.concurrency if self.max_rate > 0 else 0
        )
        self.max_delay = (
            1 / self.min_rate * self.concurrency if self.min_rate > 0 else 0
        )

    def add_latency(self, latencies: List[float]) -> None:
        """
        Add latencies to the history and update session and request counts.

        Args:
            latencies (List[float]): A list of latency values to add.
        """
        self.sessions += 1
        self.requests += len(latencies)
        self.athrottle_history.add_latency(latencies)

    def compute_stats(self) -> None:
        """
        Compute and update the current mean, standard deviation, and coefficient of variation of latency.
        """
        self.athrottle_history.compute_stats()
        if len(self.athrottle_history.latency_mean) > 0:
            self.latency_mean = self.athrottle_history.latency_mean[-1]
            self.latency_std = self.athrottle_history.latency_std[-1]
            self.latency_cv = self.athrottle_history.latency_cv[-1]

    def get_delay(self) -> float:
        """
        Compute the current delay based on the current rate.

        Returns:
            float: The computed delay in seconds.
        """
        self.delay = self._compute_delay(self.rate)
        return self.delay

    def _compute_delay(self, rate: float) -> float:
        """
        Internal method to compute delay based on the current rate and add random normal variation.

        Args:
            rate (float): The current rate of requests per second.

        Returns:
            float: The computed delay in seconds.

        Raises:
            RuntimeError: If delay computation fails.
        """
        try:
            if rate > 0:
                delay = 1 / rate * self.concurrency
            else:
                delay = 0

            delay += np.random.normal(loc=delay, scale=self.temperature, size=None)
            delay = min(delay, self.max_delay)
            delay = max(delay, self.min_delay)

            return delay

        except Exception as e:
            logging.error(f"Error computing delay: {e}")
            raise RuntimeError("Failed to compute delay.") from e

    def adjust_rate(self) -> None:
        """
        Adjust the rate based on the current stage of throttling.
        """
        self.compute_stats()
        if self.current_stage == AThrottleStatus.EXPLORE.value:
            self.rate += self.exploration_adjustment()
        elif self.current_stage == AThrottleStatus.EXPLOIT.value:
            self.rate += self.exploitation_adjustment()
        else:
            self.rate += 0

        self.rate = max(self.min_rate, min(self.max_rate, self.rate))

    def exploration_adjustment(self) -> float:
        """
        Compute the rate adjustment during the exploration stage based on the coefficient of variation.

        Returns:
            float: The adjustment to the rate.
        """
        session_cv = self.latency_cv
        historical_cv = np.mean(list(self.athrottle_history.latency_cv))

        if np.abs(session_cv - historical_cv) > self.threshold * historical_cv:
            logging.debug(
                f"Significant change in cv. Reducing rate by {self.exploration_cooldown_step_size} requests per second."
            )
            self._count_adjustments(self.exploration_cooldown_step_size)
            return self.exploration_cooldown_step_size
        else:
            logging.debug(
                f"No significant change in latency stability. Increasing rate by {self.exploration_heatup_step_size} requests per second."
            )
            self._count_adjustments(self.exploration_heatup_step_size)
            return self.exploration_heatup_step_size

    def exploitation_adjustment(self) -> float:
        """
        Compute the rate adjustment during the exploitation stage based on the mean latency.

        Returns:
            float: The adjustment to the rate.
        """
        session_mean = self.latency_mean
        historical_mean = np.mean(list(self.athrottle_history.latency_mean))

        if np.abs(session_mean - historical_mean) > self.threshold * historical_mean:
            prop_chg = self.k * (historical_mean - session_mean) / historical_mean
            logging.debug(
                f"Significant change in mean latency. Adjusting rate by {round(prop_chg, 2)}."
            )
            self._count_adjustments(prop_chg)
            return self.rate * prop_chg
        else:
            logging.debug("No significant change in mean latency. Rate unchanged.")
            return 0

    def set_stage(self) -> None:
        """
        Updates the current stage based on the elapsed time and transitions to the next stage if necessary.
        """
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        # Get the length of the current stage
        if self.current_stage == AThrottleStatus.BURNIN.value:
            stage_length = self.burnin_length
        elif self.current_stage == AThrottleStatus.EXPLORE.value:
            stage_length = self.explore_length
        else:
            stage_length = self.exploit_length

        if elapsed_time >= stage_length:
            # Move to the next stage
            self.current_stage = (self.current_stage + 1) % len(AThrottleStatus)
            self.start_time = current_time

    async def throttle(self, latencies: List[float]) -> float:
        """
        Updates the throttle state based on new latencies, adjusts the rate, and manages stage transitions.

        Args:
            latencies (List[float]): List of latencies from the latest requests.

        Returns:
            float: The computed delay based on the current rate and stage.
        """
        self.set_stage()  # Manage stage transitions
        self.add_latency(latencies)
        self.compute_stats()
        self.adjust_rate()
        delay = self.get_delay()
        await asyncio.sleep(delay)
        return self.delay

    def _count_adjustments(self, adjustment: float) -> None:
        """
        Count the number of rate adjustments, increases, and decreases.

        Args:
            adjustment (float): The amount by which the rate was adjusted.
        """
        self.rate_changes += 1
        if adjustment > 0:
            self.rate_increases += 1
        else:
            self.rate_decreases += 1
