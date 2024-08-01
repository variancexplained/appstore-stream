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
# Modified   : Thursday August 1st 2024 01:32:22 am                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Autothrottle Module"""
import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

import numpy as np
from simple_pid import PID

from appstorestream.domain.base.metric import Metric
from appstorestream.infra.base.service import InfraService

# ------------------------------------------------------------------------------------------------ #


class AThrottleStage(Enum):
    BURNIN = "BURNIN"
    EXPLORATION = "EXPLORATION"
    EXPLORATION_HEATUP = "EXPLORATION_HEATUP"
    EXPLORATION_COOLDOWN = "EXPLORATION_COOLDOWN"
    EXPLOITATION = "EXPLOITATION"
    EXPLOITATION_PID = "EXPLOITATION_PID"
    EXPLOITATION_PID_MULTIVARIATE = "EXPLOITATION_PID_MULTIVARIATE"


# ------------------------------------------------------------------------------------------------ #


class AThrottle(InfraService):
    """Base class for HTTP request throttle algorithms"""

    @abstractmethod
    async def delay(self, latencies: list) -> int:
        """Accepts a list of delays, executes a delay and returns the delay in seconds."""


# ------------------------------------------------------------------------------------------------ #


@dataclass
class AThrottleMetrics(Metric):
    current_stage: AThrottleStage
    current_delay: float = 0
    current_rate: float = 0
    current_mean_latency: float = 0
    current_std_latency: float = 0
    current_cv_latency: float = 0

    def compute_latency_metrics(self, latencies: list) -> None:
        if len(latencies) > 0:
            self.current_mean_latency = np.mean(latencies)
            self.current_std_latency = np.std(latencies)
            self.current_cv_latency = (
                self.current_std_latency / self.current_mean_latency
                if self.current_mean_latency != 0
                else 0
            )


# ------------------------------------------------------------------------------------------------ #
class AdaptiveThrottleStage(ABC):
    """Base class for a stage of adaptive throttling"""

    def __init__(
        self,
        base_rate: float,
        window_size: int,
        temperature: float,
        min_rate: float,
        max_rate: float,
        **kwargs
    ) -> None:
        self._base_rate = base_rate
        self._window_size = window_size
        self._temperature = temperature
        self._min_rate = min_rate
        self._max_rate = max_rate

        self._latencies = []
        self._metrics = AThrottleMetrics(
            current_stage=AThrottleStage.BURNIN,
            current_rate=self._base_rate,
            current_delay=1 / self._base_rate if self._base_rate != 0 else 0,
            current_mean_latency=0,
            current_std_latency=0,
            current_cv_latency=0,
        )

    async def __call__(self, latencies: list) -> AThrottleMetrics:
        """Accepts a list  of latencies and returns a metrics object containing delay.

        Args:
            latencies (list): List of latencies for a request session.

        """

    def compute_delay(self):
        # Delay is the inverse of rate.
        self._metrics.current_delay = (
            1 / self._metrics.current_rate if self._metrics.current_rate != 0 else 0
        )
        # Apply temperature to the std latency to determine range of noise magnitude
        noise_range = self._metrics.current_std_latency * self._temperature
        # Add noise to current delay
        self._metrics.current_delay += np.random.uniform(-noise_range, noise_range)
        self._metrics.current_delay = max(self._metrics.current_delay, self._min_rate)
        self._metrics.current_delay = min(self._metrics.current_delay, self._max_rate)

    def add_latency(self, latencies: list) -> None:
        self._latencies.extend(latencies)
        if len(self._latencies) > self._window_size:
            self._latencies = self._latencies[-self._window_size :]


# ------------------------------------------------------------------------------------------------ #
class BurningStage(AdaptiveThrottleStage):
    """Burn in stage is designed to learn the baseline latency statistics."""

    __current_stage = AThrottleStage.BURNIN

    def __init__(
        self,
        base_rate: float,
        window_size: int,
        temperature: float,
        min_rate: float,
        max_rate: float,
        **kwargs
    ) -> None:
        super().__init__(
            base_rate=base_rate,
            window_size=window_size,
            temperature=temperature,
            min_rate=min_rate,
            max_rate=max_rate,
        )

    async def __call__(self, latencies: List[float]) -> AThrottleMetrics:
        self.add_latencies(latencies)
        # Compute metrics with the current latencies
        self._metrics.compute_latency_metrics(self.latencies)
        # Here, no rate adjustment is typically made during burnin stage
        self.compute_delay()
        return self._metrics


# ------------------------------------------------------------------------------------------------ #
class ExplorationStage(AdaptiveThrottleStage):
    def __init__(
        self,
        base_rate: float,
        window_size: int,
        heatup_factor: float,
        cooldown_factor: float,
        exploration_threshold: float,
        temperature: float,
        min_rate: float,
        max_rate: float,
    ):
        super().__init__(
            base_rate=base_rate,
            temperature=temperature,
            min_rate=min_rate,
            max_rate=max_rate,
            window_size=window_size,
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
        error = self.setpoint - current_value
        current_time = time.time()
        delta_time = current_time - self._last_time

        if delta_time >= self.sample_time:
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
        min_rate: float,
        max_rate: float,
        sample_time: int,  # Time in seconds to wait before returning metrics
    ):
        super().__init__(
            base_rate=min_rate,  # Initialize base_rate as min_rate
            temperature=temperature,
            min_rate=min_rate,
            max_rate=max_rate,
            window_size=sample_time,
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
            self._metrics.current_rate = (
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
        min_rate: float,
        max_rate: float,
        sample_time: int,  # Time in seconds to wait before returning metrics
    ):
        super().__init__(
            base_rate=min_rate,  # Initialize base_rate as min_rate
            temperature=temperature,
            min_rate=min_rate,
            max_rate=max_rate,
            window_size=sample_time,
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


class ExploitationPIDSimple(AdaptiveThrottleStage):
    def __init__(
        self,
        target_latency: float,
        kp: float,
        ki: float,
        kd: float,
        temperature: float,
        min_rate: float,
        max_rate: float,
        sample_time: int,  # Time in seconds to wait before returning metrics
    ):
        super().__init__(
            base_rate=min_rate,
            temperature=temperature,
            min_rate=min_rate,
            max_rate=max_rate,
            window_size=sample_time,
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


class ThrottleController:
    def __init__(
        self,
        stages: Dict[AThrottleStage, AdaptiveThrottleStage],
        initial_stage: AThrottleStage = AThrottleStage.BURNIN,
    ):
        self.stages = stages
        self.current_stage = initial_stage
        self.active_stage = self.stages[self.current_stage]

    async def process_latencies(self, latencies: List[float]) -> AThrottleMetrics:
        # Process latencies using the active stage
        metrics = await self.active_stage(latencies)

        # Check if a transition to a different stage is needed
        self._handle_stage_transition()

        return metrics

    def _handle_stage_transition(self):
        new_stage = self._determine_next_stage()
        if new_stage != self.current_stage:
            self.current_stage = new_stage
            self.active_stage = self.stages[self.current_stage]

    def _determine_next_stage(self) -> AThrottleStage:
        # Logic to determine the next stage based on current metrics and stage
        if self.current_stage == AThrottleStage.BURNIN:
            if (
                self.stages[AThrottleStage.BURNIN]._current_stage
                == AThrottleStage.EXPLORATION
            ):
                return AThrottleStage.EXPLORATION
        elif self.current_stage == AThrottleStage.EXPLORATION:
            if (
                self.stages[AThrottleStage.EXPLORATION]._current_stage
                == AThrottleStage.EXPLOITATION
            ):
                return AThrottleStage.EXPLOITATION_PID
        elif self.current_stage == AThrottleStage.EXPLOITATION_PID:
            # You may add conditions for transitioning to the multivariate PID stage if needed
            pass
        elif self.current_stage == AThrottleStage.EXPLOITATION_PID_MULTIVARIATE:
            # Final stage logic or transitions to other stages
            pass

        return self.current_stage

    def set_stage(self, stage: AThrottleStage):
        if stage in self.stages:
            self.current_stage = stage
            self.active_stage = self.stages[stage]

    async def run(self, latencies: List[float]):
        while True:
            metrics = await self.process_latencies(latencies)
            # Handle metrics or other logic if needed
            await asyncio.sleep(1)  # Adjust sleep time as needed
