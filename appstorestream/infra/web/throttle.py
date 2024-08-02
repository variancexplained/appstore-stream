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
# Modified   : Friday August 2nd 2024 12:30:34 am                                                  #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Autothrottle Module"""
from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
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
    mean_latency: float = 0
    std_latency: float = 0
    cv_latency: float = 0
    rate: float = 0
    delay: float = 0


# ------------------------------------------------------------------------------------------------ #
class AThrottleState(Enum):
    BURNIN = "BURNIN"
    EXPLORE = "EXPLORE"
    EXPLOIT = "EXPLOIT"


# ------------------------------------------------------------------------------------------------ #
class AThrottleStage(InfraService):
    """Base class for HTTP request throttle stage algorithms"""

    def __init__(
        self,
        controller: AThrottleController,
        stage_length: int = 50,
        temperature: float = 0.5,
        concurrency: int = 100,
        base_rate: int = 100,
        min_rate: int = 50,
        max_rate: int = 1000,
        metrics: AThrottleMetrics = None,
        **kwargs,
    ) -> None:
        self._controller = controller
        self._stage_length = stage_length
        self._temperature = temperature
        self._concurrency = concurrency
        self._base_rate = base_rate
        self._min_rate = min_rate
        self._max_rate = max_rate
        self._metrics = metrics

        self._kwargs = kwargs
        self._latencies = []

        self._start_time = None
        # Compute min and max delay
        self._min_delay = 1 / self._max_rate
        self._max_delay = 1 / self._min_rate

    @property
    def controller(self) -> AThrottleController:
        return self._controller

    @abstractmethod
    async def delay(self, latencies: list) -> AThrottleMetrics:
        """Accepts a list of delays, executes a delay and returns the delay in seconds."""

    @abstractmethod
    async def add_latencies(self, latencies: list) -> AThrottleMetrics:
        """Adds latencies to the latencies list. Subclasses may use different latency window sizes."""

    def compute_delay(self) -> float:
        # Presumes a metrics object and that the rate member reflects the current request rate.
        self._metrics.delay = 1 / self._metrics.rate if self._metrics.rate > 0 else 0
        # Add noise to current delay
        self._metrics.delay += np.random.normal(
            loc=self._metrics.delay, scale=self._temperature, size=None
        )
        self._metrics.delay = max(self._metrics.delay, self._metrics.min_delay)
        self._metrics.delay = min(self._metrics.delay, self._metrics.max_delay)

    def compute_metrics(self) -> None:
        """Computes latency mean, standard deviation and coefficient of variation in the metrics object"""
        self._metrics.mean_latency = np.mean(self._latencies)
        self._metrics.std_latency = np.std(self._latencies)
        self._cv_latency = (
            self._std_latency / self._mean_latency if self._mean_latency > 0 else 0
        )

    def has_expired(self) -> bool:
        self._start_time = self._start_time or time.time()
        return (time.time() - self._start_time) > self._stage_length * 60


# ------------------------------------------------------------------------------------------------ #
class BurningStage(AThrottleStage):
    """Burn in stage is designed to learn the baseline latency statistics."""

    def __init__(
        self,
        controller: AThrottleController,
        stage_length: int = 50,
        temperature: float = 0.5,
        concurrency: int = 100,
        burnin_rate: int = 100,
        min_rate: int = 50,
        max_rate: int = 1000,
        **kwargs,
    ) -> None:
        super().__init__(
            controller=controller,
            stage_length=stage_length,
            temperature=temperature,
            concurrency=concurrency,
            min_rate=min_rate,
            max_rate=max_rate,
            **kwargs,
        )
        self._burnin_rate = burnin_rate
        self._metrics = AThrottleMetrics(rate=self._burnin_rate)

    async def delay(self, latencies: list) -> int:
        """Accepts a list of delays, executes a delay and returns the delay in seconds."""
        if self.has_expired():
            self._controller.stage = AThrottleStage.EXPLORE
            return self._metrics
        else:
            self.compute_metrics(latencies=latencies)
            self.compute_delay()
            return self._metrics

    def add_latencies(self, latencies: List) -> None:
        self._latencies.extend(latencies)


# ------------------------------------------------------------------------------------------------ #
class ExplorationStage(AdaptiveThrottleStage):
    def __init__(
        self,
        base_delay: float,
        session_window_size: int,
        heatup_factor: float,
        cooldown_factor: float,
        exploration_threshold: float,
        temperature: float,
        min_delay: float,
        max_delay: float,
    ):
        super().__init__(
            base_delay=base_delay,
            temperature=temperature,
            min_delay=min_delay,
            max_delay=max_delay,
            session_window_size=session_window_size,
        )
        self.heatup_factor = heatup_factor
        self.cooldown_factor = cooldown_factor
        self.exploration_threshold = exploration_threshold
        self._baseline_mean_latency = None
        self._baseline_std_latency = None
        self._baseline_cv_latency = None
        self._current_stage = AThrottleStage.BURNIN  # Initially in the burnin stage

    async def __call__(self, latencies: List[float]) -> AThrottleMetrics:
        self.add_latencies(latencies)
        self._metrics.compute_latency_metrics(self.latencies)

        if self._is_stable():
            if self._current_stage == AThrottleStage.EXPLORATION_HEATUP:
                self._metrics.current_rate += self.heatup_factor
            else:
                self._reset_baseline()
                self._current_stage = AThrottleStage.EXPLOITATION
        else:
            self._metrics.current_rate -= self.cooldown_factor
            self._current_stage = AThrottleStage.EXPLORATION_COOLDOWN

        self.compute_delay()
        return self._metrics

    def _is_stable(self) -> bool:
        return (
            (
                self._baseline_mean_latency is None
                or self._metrics.current_mean_latency
                <= self._baseline_mean_latency * self.exploration_threshold
            )
            and (
                self._baseline_std_latency is None
                or self._metrics.current_std_latency
                <= self._baseline_std_latency * self.exploration_threshold
            )
            and (
                self._baseline_cv_latency is None
                or self._metrics.current_cv_latency
                <= self._baseline_cv_latency * self.exploration_threshold
            )
        )

    def _reset_baseline(self):
        self._baseline_mean_latency = self._metrics.current_mean_latency
        self._baseline_std_latency = self._metrics.current_std_latency
        self._baseline_cv_latency = self._metrics.current_cv_latency


# ------------------------------------------------------------------------------------------------ #
class PIDController:

    def __init__(
        self,
        setpoint: float,
        Kp: float = 0.1,
        Ki: float = 0.01,
        Kd: float = 0.05,
        sample_time: float = 1.0,
    ):
        """
        PID controller initialization.

        Args:
            setpoint (float): The desired value.
            Kp (float): Proportional gain.
            Ki (float): Integral gain.
            Kd (float): Derivative gain.
            sample_time (float): Time (in seconds) between updates.
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.sample_time = sample_time

        self._prev_error = 0
        self._integral = 0
        self._last_time = time.time()

    def update(self, current_value):
        """
        Update the PID controller.

        Args:
            current_value (float): The current value to compare to the setpoint.

        Returns:
            float: The control output to adjust the process.
        """

        current_time = time.time()
        delta_time = current_time - self._last_time

        if delta_time >= self.sample_time:
            error = self.setpoint - current_value
            self._integral += error * delta_time
            derivative = (
                (error - self._prev_error) / delta_time if delta_time > 0 else 0
            )

            output = (
                (self.Kp * error) + (self.Ki * self._integral) + (self.Kd * derivative)
            )

            self._prev_error = error
            self._last_time = current_time

            return output
        return 0


# ------------------------------------------------------------------------------------------------ #
class ExploitationPID(AdaptiveThrottleStage):
    def __init__(
        self,
        target_latency: float,
        kp: float,
        ki: float,
        kd: float,
        temperature: float,
        min_delay: float,
        max_delay: float,
        sample_time: int,  # Time in seconds to wait before returning metrics
    ):
        super().__init__(
            base_delay=min_delay,  # Initialize base_delay as min_delay
            temperature=temperature,
            min_delay=min_delay,
            max_delay=max_delay,
            session_window_size=sample_time,
        )
        self.target_latency = target_latency
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.previous_error = 0
        self.sample_time = sample_time  # Sample time in seconds
        self.last_update_time = time.time()

    async def __call__(self, latencies: List[float]) -> AThrottleMetrics:
        current_time = time.time()
        if (current_time - self.last_update_time) >= self.sample_time:
            current_mean_latency = np.mean(latencies)
            error = self.target_latency - current_mean_latency
            self.integral += error
            derivative = error - self.previous_error
            self.previous_error = error

            # PID calculation for rate adjustment
            self._metrics.current_delay = (
                self.kp * error + self.ki * self.integral + self.kd * derivative
            )

            self.compute_delay()
            self.compute_metrics(latencies)
            self.last_update_time = current_time  # Update the last update time

        return self._metrics


# ------------------------------------------------------------------------------------------------ #


class ExploitationPIDMultivariate(AdaptiveThrottleStage):
    def __init__(
        self,
        target_mean_latency: float,
        target_std_latency: float,
        target_cv_latency: float,
        kp_mean: float,
        ki_mean: float,
        kd_mean: float,
        kp_std: float,
        ki_std: float,
        kd_std: float,
        kp_cv: float,
        ki_cv: float,
        kd_cv: float,
        temperature: float,
        min_delay: float,
        max_delay: float,
        sample_time: int,  # Time in seconds to wait before returning metrics
    ):
        super().__init__(
            base_delay=min_delay,  # Initialize base_delay as min_delay
            temperature=temperature,
            min_delay=min_delay,
            max_delay=max_delay,
            session_window_size=sample_time,
        )
        self.target_mean_latency = target_mean_latency
        self.target_std_latency = target_std_latency
        self.target_cv_latency = target_cv_latency
        self.kp_mean = kp_mean
        self.ki_mean = ki_mean
        self.kd_mean = kd_mean
        self.kp_std = kp_std
        self.ki_std = ki_std
        self.kd_std = kd_std
        self.kp_cv = kp_cv
        self.ki_cv = ki_cv
        self.kd_cv = kd_cv
        self.integral_mean = 0
        self.integral_std = 0
        self.integral_cv = 0
        self.previous_error_mean = 0
        self.previous_error_std = 0
        self.previous_error_cv = 0
        self.sample_time = sample_time  # Sample time in seconds
        self.last_update_time = time.time()

    async def __call__(self, latencies: List[float]) -> AThrottleMetrics:
        current_time = time.time()
        if (current_time - self.last_update_time) >= self.sample_time:
            current_mean_latency = np.mean(latencies)
            current_std_latency = np.std(latencies)
            current_cv_latency = (
                current_std_latency / current_mean_latency
                if current_mean_latency > 0
                else 0
            )

            # PID calculations for rate adjustments
            error_mean = self.target_mean_latency - current_mean_latency
            self.integral_mean += error_mean
            derivative_mean = error_mean - self.previous_error_mean
            self.previous_error_mean = error_mean

            error_std = self.target_std_latency - current_std_latency
            self.integral_std += error_std
            derivative_std = error_std - self.previous_error_std
            self.previous_error_std = error_std

            error_cv = self.target_cv_latency - current_cv_latency
            self.integral_cv += error_cv
            derivative_cv = error_cv - self.previous_error_cv
            self.previous_error_cv = error_cv

            self._metrics.current_rate = (
                self.kp_mean * error_mean
                + self.ki_mean * self.integral_mean
                + self.kd_mean * derivative_mean
                + self.kp_std * error_std
                + self.ki_std * self.integral_std
                + self.kd_std * derivative_std
                + self.kp_cv * error_cv
                + self.ki_cv * self.integral_cv
                + self.kd_cv * derivative_cv
            )

            self.compute_delay()
            self.compute_metrics(latencies)
            self.last_update_time = current_time  # Update the last update time

        return self._metrics


# ------------------------------------------------------------------------------------------------ #


class ExploitationPIDSimple(AThrottleStage):
    def __init__(
        self,
        target_latency: float,
        kp: float,
        ki: float,
        kd: float,
        temperature: float,
        min_delay: float,
        max_delay: float,
        sample_time: int,  # Time in seconds to wait before returning metrics
    ):
        super().__init__(
            base_delay=min_delay,
            temperature=temperature,
            min_delay=min_delay,
            max_delay=max_delay,
            session_window_size=sample_time,
        )
        self.target_latency = target_latency
        self.pid = PID(kp, ki, kd, setpoint=target_latency)
        self.sample_time = sample_time
        self.last_update_time = time.time()

    async def __call__(self, latencies: List[float]) -> AThrottleMetrics:
        current_time = time.time()
        if (current_time - self.last_update_time) >= self.sample_time:
            current_mean_latency = np.mean(latencies)

            # Compute new output from the PID according to the current mean latency
            control = self.pid(current_mean_latency)

            # Adjust rate based on PID output
            self._metrics.current_rate = control

            self.compute_delay()
            self.compute_metrics(latencies)
            self.last_update_time = current_time  # Update the last update time

        return self._metrics


# ------------------------------------------------------------------------------------------------ #


class AThrottleController:

    def __init__(self, config: dict) -> None:
        self._config = config
        self._state = AThrottleState.BURNIN

    @property
    def state(self) -> AThrottleState:
        return self._state

    @state.setter
    def state(self, state: AThrottleState) -> None:
        self._state = state
