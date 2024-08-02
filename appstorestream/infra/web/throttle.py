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
# Modified   : Friday August 2nd 2024 09:16:42 am                                                  #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Autothrottle Module"""
from __future__ import annotations

import asyncio
import copy
import logging
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List

import numpy as np
import pandas as pd
from simple_pid import PID

from appstorestream.domain.base.metric import Metric
from appstorestream.infra.base.service import InfraService


# ------------------------------------------------------------------------------------------------ #
@dataclass
class AThrottleMetrics(Metric):
    """
    A class to track and compute metrics for throttling requests.

    Attributes:
        window_size (int): Number of latency records to consider for the window. Default is 60000.
        threshold (float): Factor of baseline stats required for a stable rating. Default is 1.2.
        temperature (float): Controls the amount of random noise in the delay.
        latency (deque): Deque storing latency records with a maximum length of 300,000.
        baseline_mean_latency (float): Computed mean latency during the burn-in period. Default is 0.
        baseline_std_latency (float): Computed standard deviation of latency during the burn-in period. Default is 0.
        baseline_cv_latency (float): Coefficient of variation of latency during the burn-in period. Default is 0.
        current_rate (float): Current request rate. Default is 0.
        current_delay (float): Current delay between requests. Default is 0.
    """

    latency: deque = field(default_factory=lambda: deque(maxlen=300000))
    window_size: int = (
        60000  # Approximately 1 minute of data at 100 requests per second.
    )
    threshold: float = 1.2  # The factor of baseline stats required for a stable rating.
    temperature: float = 0.5  # Controls the amount of random noise in the delay
    baseline_mean_latency: float = 0  # Baseline figures computed during burn-in.
    baseline_std_latency: float = 0
    baseline_cv_latency: float = 0
    current_rate: float = 0  # Current rate and delay.
    current_delay: float = 0
    min_rate: int = 50  # Minimum rate of requests per second
    max_rate: int = 1000  # Maximum rate of requests per second
    modified: float = None  # Number of seconds since the epoch.

    def add_latency(self, latencies: list) -> None:
        """
        Adds latency records to the deque.

        Args:
            latencies (list): List of latency values to be added to the deque.
        """
        if not isinstance(latencies, list):
            raise TypeError("latencies should be a list of numbers.")
        if not (isinstance(latency, (int, float)) for latency in latencies):
            raise ValueError("All latency values must be integers or floats.")
        self.latency.extend(latencies)

    def compute_baseline_stats(self) -> None:
        """
        Computes baseline statistics (mean, standard deviation, and coefficient of variation) from latency data.

        Raises:
            ValueError: If the latency deque is empty.
            RuntimeError: If an error occurs during statistics computation.
        """
        if len(self.latency) == 0:
            raise ValueError(
                "No latency values available to compute baseline statistics."
            )
        if (
            self.baseline_mean_latency == 0
            and self.baseline_std_latency == 0
            and self.baseline_cv_latency == 0
        ):
            try:
                self.baseline_mean_latency = np.mean(self.latency)
                self.baseline_std_latency = np.std(self.latency)
                self.baseline_cv_latency = (
                    self.baseline_std_latency / self.baseline_mean_latency
                    if self.baseline_mean_latency > 0
                    else 0
                )
            except Exception as e:
                logging.error(f"Error computing baseline metrics: {e}")
                raise RuntimeError("Failed to compute baseline metrics.") from e
        else:
            print("Baseline metrics have already been computed.")

    def stabilized(self) -> bool:
        """
        Determines whether the current coefficient of variation (CoV) is within the threshold of the baseline.

        Returns:
            bool: True if the current CoV is below the threshold times baseline CoV, False otherwise.

        Raises:
            ValueError: If the latency deque does not contain enough data to evaluate stability.
            RuntimeError: If an error occurs during computation.
        """
        try:
            # Extract the most recent `window_size` records
            current_window = list(self.latency)[-self.window_size :]
            if len(current_window) == 0:
                raise ValueError("The current window has no data to compute stability.")

            current_mean_latency = np.mean(current_window)
            current_std_latency = np.std(current_window)
            current_cv_latency = (
                current_std_latency / current_mean_latency
                if current_mean_latency > 0
                else 0
            )

            # Compare current CoV with baseline CoV
            stabilized = current_cv_latency < self.baseline_cv_latency * self.threshold
            return stabilized

        except (TypeError, ValueError, np.AxisError) as e:
            logging.error(f"Error evaluating stability: {e}")
            raise RuntimeError("Failed to compute stability metrics.") from e
        except Exception as e:
            logging.error(f"Unexpected error in stabilized: {e}")
            raise RuntimeError(
                "An unexpected error occurred while evaluating stability."
            ) from e

    def compute_delay(self) -> None:
        """
        Computes the current delay based on the current rate and adds random noise to simulate variability.

        Raises:
            RuntimeError: If an error occurs during delay computation.
        """

        try:
            # Compute min and max delay
            min_delay = 1 / self.max_rate if self.max_rate > 0 else 0
            max_delay = 1 / self.min_rate if self.min_rate > 0 else 0

            if self.current_rate > 0:
                self.current_delay = 1 / self.current_rate
            else:
                self.current_delay = 0

            # Add noise to current delay
            self.current_delay += np.random.normal(
                loc=self.current_delay, scale=self.temperature, size=None
            )
            self.current_delay = min(self.current_delay, max_delay)
            self.current_delay = max(self.current_delay, min_delay)

        except Exception as e:
            logging.error(f"Error computing delay: {e}")
            raise RuntimeError("Failed to compute delay.") from e


# ------------------------------------------------------------------------------------------------ #
class AThrottleStatus(Enum):
    BURNIN = "BURNIN"
    EXPLORE = "EXPLORE"
    EXPLOIT = "EXPLOIT"


# ------------------------------------------------------------------------------------------------ #
class AThrottleStage(InfraService):
    """Base class for HTTP request throttle stage algorithms.

    Args:
        metrics (AThrottleMetrics, optional): An optional metrics instance for tracking throttling metrics.
        controller (AThrottleController): The controller instance to manage throttling.
        stage_length (int, optional): The length of the stage in minutes. Defaults to 50.
        temperature (float, optional): The temperature parameter for adding noise to delay. Defaults to 0.5.
        min_rate (int, optional): The minimum rate of requests per second. Defaults to 50.
        max_rate (int, optional): The maximum rate of requests per second. Defaults to 1000.
        **kwargs: Additional keyword arguments.

    """

    def __init__(
        self,
        metrics: AThrottleMetrics,
        controller: AThrottleController,
        stage_length: int = 50,
        **kwargs,
    ) -> None:
        self._metrics = metrics
        self._controller = controller
        self._stage_length = stage_length

        self._kwargs = kwargs
        self._start_time = None

        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def controller(self) -> AThrottleController:
        """Returns the throttle controller instance."""
        return self._controller

    @property
    def metrics(self) -> AThrottleController:
        """Returns the metrics instance."""
        return self._metrics

    @abstractmethod
    async def __call__(self, latencies: list) -> AThrottleMetrics:
        """Accepts a list of delays, executes a delay, and returns the delay in seconds.

        Args:
            latencies (list): List of latency values.

        Returns:
            AThrottleMetrics: Updated throttle metrics.
        """
        pass

    def stage_expired(self) -> bool:
        """Checks if the current stage has expired based on the start time and stage length.

        Returns:
            bool: True if the stage has expired, False otherwise.
        """
        try:
            self._start_time = self._start_time or time.time()
            return (time.time() - self._start_time) > self._stage_length
        except Exception as e:
            self._logger.error(f"Error checking if stage has expired: {e}")
            raise


# ------------------------------------------------------------------------------------------------ #
class BurninStage(AThrottleStage):
    """Burn-in stage designed to learn and compute baseline latency statistics.

    During the burn-in phase, latency data is collected to establish baseline statistics.
    The stage then transitions to the explore phase when the burn-in period ends.
    """

    def __init__(
        self,
        metrics: AThrottleMetrics,
        controller: AThrottleController,
        stage_length: int = 50,
        **kwargs,
    ) -> None:
        """
        Initializes the BurninStage.

        Args:
            metrics (AThrottleMetrics): The metrics object used for tracking latency and computing statistics.
            controller (AThrottleController): The controller managing the throttle stages.
            stage_length (int, optional): The duration of the burn-in stage in minutes. Defaults to 50 minutes.
            **kwargs: Additional keyword arguments to pass to the parent class.

        Raises:
            ValueError: If metrics or controller is not provided.
        """
        if metrics is None:
            raise ValueError("AThrottleMetrics instance must be provided.")
        if controller is None:
            raise ValueError("AThrottleController instance must be provided.")

        super().__init__(
            metrics=metrics,
            controller=controller,
            stage_length=stage_length,
            **kwargs,
        )

    async def __call__(self, latencies: list) -> int:
        """
        Processes a list of latencies, executes a delay based on the computed metrics,
        and updates the stage status upon completion of the burn-in phase.

        Args:
            latencies (list): List of latency values to be added to the metrics.

        Returns:
            int: Status code indicating the outcome of the processing.

        Raises:
            ValueError: If latencies is not a list.
            Exception: If any error occurs during delay computation or statistics updating.
        """

        try:
            self._metrics.add_latency(latencies=latencies)
            self._metrics.compute_delay()
            await asyncio.sleep(self._metrics.current_delay)

            if self.stage_expired():
                self._metrics.compute_baseline_stats()
                self._controller.state = AThrottleStatus.EXPLORE

            return 0  # Status code indicating successful processing

        except Exception as e:
            logging.error(f"Error during burn-in stage processing: {e}")
            raise


# ------------------------------------------------------------------------------------------------ #
class ExplorationStage(AThrottleStage):
    """Exploration stage optimizes delay while monitoring server stability."""

    def __init__(
        self,
        metrics: AThrottleMetrics,
        controller: AThrottleController,
        observation_period: int = 3,
        heatup_factor: int = 50,
        cooldown_factor: int = 10,
        stage_length: int = 5,
        **kwargs,
    ) -> None:
        super().__init__(
            metrics=metrics,
            controller=controller,
            stage_length=stage_length,
            **kwargs,
        )
        self._observation_period = observation_period
        self._heatup_factor = heatup_factor
        self._cooldown_factor = cooldown_factor

        self._in_heatup = True

    async def __call__(self, latencies: list) -> int:
        """Accepts a list of delays, executes a delay and returns the delay in seconds."""
        self._metrics.add_latency(latencies=latencies)

        if self.in_observation():
            pass
        else:
            if self._metrics.stabilized():
                # If in heatup continue to increase rate
                if self._in_heatup:
                    self.bump_rate()
                else:
                    self._controller.state = AThrottleStatus.EXPLOIT
            else:
                self._in_heatup = False
                self.backoff_rate()

        self._metrics.compute_delay()
        await asyncio.sleep(self._metrics.current_delay)

    def in_observation(self) -> bool:
        """Returns true if the current time is within our observation period."""
        if not self._metrics.modified:
            return False
        return (time.time() - self._metrics.modified) < self._observation_period

    def bump_rate(self) -> None:
        """Increases the rate by the heatup factor"""

        orig = self._metrics.current_rate
        self._metrics.current_rate += self._heatup_factor
        self._metrics.modified = time.time()
        pct_increase = round(
            (self._metrics.current_rate - orig) / orig * 100,
            2,
        )

        self._logger.debug(
            f"Increased request rate by {pct_increase}% from {orig} to {self._metrics.current_rate}."
        )

    def backoff_rate(self) -> None:
        """Decreases the rate by the cooldown factor"""

        orig = self._metrics.current_rate
        self._metrics.current_rate -= self._cooldown_factor
        self._metrics.modified = time.time()
        pct_decrease = round(
            (orig - self._metrics.current_rate) / orig * 100,
            2,
        )
        self._logger.debug(
            f"Decreased request rate by {pct_decrease}% from {orig} to {self._metrics.current_rate}."
        )


# ------------------------------------------------------------------------------------------------ #


class AThrottleController:

    def __init__(self, config: dict) -> None:
        self._config = config
        self._state = AThrottleStatus.BURNIN

    @property
    def state(self) -> AThrottleStatus:
        return self._state

    @state.setter
    def state(self, state: AThrottleStatus) -> None:
        self._state = state


# ------------------------------------------------------------------------------------------------ #
class AThrottle:
    """Dummy class for construction purposes"""
