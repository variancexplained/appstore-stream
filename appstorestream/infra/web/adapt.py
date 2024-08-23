#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/web/adapt.py                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 04:44:47 am                                                   #
# Modified   : Friday August 23rd 2024 07:58:30 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Autothrottle Module"""
from __future__ import annotations

import asyncio
import logging
import statistics
import time
from abc import ABC, abstractmethod
from typing import Mapping, Optional, Union

import numpy as np

from appstorestream.core.data import NestedNamespace
from appstorestream.infra.web.profile import (
    SessionControl,
    SessionHistory,
    SessionStats,
    StatisticalSnapshot,
)


# ------------------------------------------------------------------------------------------------ #
#                                ADAPTER VALUE MIXIN                                               #
# ------------------------------------------------------------------------------------------------ #
class Clock:
    def __init__(self) -> None:
        self._start_time: Optional[float] = 0.0

    def start(self) -> None:
        """Starts or restarts the clock."""
        self._start_time = time.time()

    def reset(self) -> None:
        """Resets the clock to zero."""
        self._start_time = 0.0

    def elapsed(self) -> float:
        """Returns the time elapsed since the clock was started or last reset."""
        if self._start_time is None:
            raise RuntimeError("Clock has not been started.")
        return time.time() - self._start_time

    def has_elapsed(self, duration: float) -> bool:
        """Checks if a given duration has elapsed."""
        return self.elapsed() >= duration

    def is_active(self) -> bool:
        """Returns true if clock is active."""
        return self._start_time != 0.0


# ------------------------------------------------------------------------------------------------ #
#                                ADAPTER VALUE MIXIN                                               #
# ------------------------------------------------------------------------------------------------ #
class SessionControlValue:
    """Class to handle session control values such as request rate and concurrency.

    This mixin provides functionality to manage a value that can be
    increased or decreased based on defined additive and multiplicative
    factors while respecting minimum and maximum constraints. It can be
    used in various stages or adapters where such adaptive behavior is needed.

    Attributes:
        -initial_value (float): The initial value
        _value (float): The current value.
        _min_value (float): The minimum allowable value.
        _max_value (float): The maximum allowable value.
        _additive_factor (float): The value to add when increasing.
        _multiplicative_factor (float): The factor by which to multiply when decreasing.
        _temperature (float): The standard deviation of the noise added to the value.
    """

    def __init__(
        self,
        initial_value: float,
        min_value: float,
        max_value: float,
        additive_factor: float = 0.0,
        multiplicative_factor: float = 1.0,
        temperature: float = 0.0,
    ) -> None:
        """Initialize the SessionControlValue with initial and constraint values.

        Args:
            initial_value (float): The starting value of the adaptive value.
            min_value (float): The minimum limit for the adaptive value.
            max_value (float): The maximum limit for the adaptive value.
            additive_factor (float): The value to be added for increase operations. Default = 0.9
            multiplicative_factor (float): The factor to be multiplied for decrease operations. Default = 1.0
            temperature (float, optional): The standard deviation of the noise to add to the value. Defaults to 0.0.
        """
        self._initial_value = initial_value
        self._value = initial_value
        self._min_value = min_value
        self._max_value = max_value
        self._additive_factor = additive_factor
        self._multiplicative_factor = multiplicative_factor
        self._temperature = temperature
        self._values: list[float] = []

    @property
    def value(self) -> float:
        """Get the current value.

        Returns:
            float: The current adaptive value.
        """
        return self._value

    @property
    def median_value(self) -> float:
        """Get the maximum value returned in the current stage

        Returns:
            float: The current maximum value
        """
        return statistics.median(self._values)

    def increase_value(self) -> None:
        """Increase the value additively, respecting min/max constraints.

        The current value is increased by the additive factor plus noise,
        and if the resulting value exceeds the maximum allowable value,
        it is set to the maximum value.
        """
        noise = np.random.normal(loc=0, scale=self._temperature)
        new_value = self._value + self._additive_factor + noise
        self._value = min(new_value, self._max_value)
        self._values.append(self._value)

    def decrease_value(self) -> None:
        """Decrease the value multiplicatively, respecting min/max constraints.

        The current value is multiplied by the multiplicative factor plus noise,
        and if the resulting value falls below the minimum allowable value,
        it is set to the minimum value.
        """
        noise = np.random.normal(loc=0, scale=self._temperature)
        new_value = self._value * self._multiplicative_factor + noise
        self._value = max(new_value, self._min_value)
        self._values.append(self._value)

    def reset_value(self) -> None:
        """Reset value to the initial value.

        This method restores the adaptive value to its initial value as set
        during the initialization of the mixin.
        """
        self._value = self._initial_value
        self._values = []

    def add_noise(self) -> None:
        """Add noise to the current value based on the temperature."""
        noise = np.random.normal(loc=0, scale=self._temperature)
        self._value += noise
        # Ensure value stays within min/max bounds
        self._value = min(max(self._value, self._min_value), self._max_value)


# ------------------------------------------------------------------------------------------------ #
#                                        ADAPTER                                                   #
# ------------------------------------------------------------------------------------------------ #
class Adapter:

    def __init__(self, initial_stage: AdapterBaselineStage) -> None:
        self.stage = initial_stage
        self._baseline_snapshot: Optional[StatisticalSnapshot] = None
        self._session_control: SessionControl = SessionControl()
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    @property
    def session_control(self) -> SessionControl:
        return self._session_control

    @session_control.setter
    def session_control(self, session_control: SessionControl) -> None:
        if not isinstance(session_control, SessionControl):
            msg = f"Type Error: session_control is not a valid SessionControl object."
            self._logger.exception(msg)
            raise TypeError(msg)
        self._session_control = session_control

    @property
    def stage(self) -> AdapterStage:
        return self._stage

    @stage.setter
    def stage(self, stage: AdapterStage) -> None:
        if not isinstance(stage, AdapterStage):
            msg = f"Type Error: stage is not a valid AdapterStage object."
            self._logger.exception(msg)
            raise TypeError(msg)
        self._stage = stage

    @property
    def baseline_snapshot(self) -> Optional[StatisticalSnapshot]:
        return self._baseline_snapshot

    @baseline_snapshot.setter
    def baseline_snapshot(self, baseline_snapshot: StatisticalSnapshot) -> None:
        self._baseline_snapshot = baseline_snapshot

    @abstractmethod
    async def adapt(self, history: SessionHistory) -> None:
        """Computes the adapted value and sets the appropriate property."""

    def transition(self, stage: AdapterStage) -> None:
        self._logger.info(
            f"{self.__class__.__name__} transitioning from {self._stage.__class__.__name__} to {stage.__class__.__name__}"
        )
        self._stage = stage
        self._stage.adapter = self


# ------------------------------------------------------------------------------------------------ #
#                                     ADAPTER STAGE                                                #
# ------------------------------------------------------------------------------------------------ #
class AdapterStage(ABC):
    """Abstract base class for Adapter stages.

    Defines the interface and common properties for different stages of an adapter.
    Each stage handles rate and concurrency adjustments, transitioning to the next
    stage, and validation of the adapter and history objects.

    Args:
        config (Mapping[str, Union[int, float]]): Configuration parameters for the stage.

    Attributes:
        _config (NestedNamespace): A nested namespace object containing the configuration parameters.
        rate (float): The current rate, default is 50.
        concurrency (float): The current concurrency, default is 50.
        adapter (Optional[Adapter]): The current adapter associated with the stage, initially None.
        _logger (logging.Logger): Logger instance for the class.
    """

    def __init__(self, config: Mapping[str, Union[int, float]]) -> None:
        self._config = NestedNamespace(config)
        self._adapter: Optional[Adapter] = None
        self._session_history: Optional[SessionHistory] = None
        self._stage_clock = Clock()
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    @property
    def adapter(self) -> Optional[Adapter]:
        """Gets the current adapter.

        Returns:
            Optional[Adapter]: The current adapter instance, or None if no adapter has been set.
        """
        return self._adapter

    @adapter.setter
    def adapter(self, adapter: Adapter) -> None:
        """Sets the adapter after validating it.

        This setter validates the provided adapter before assigning it to the internal attribute.

        Args:
            adapter (Adapter): The adapter instance to set. It can be None if no adapter is assigned.

        Raises:
            RuntimeError: If the provided adapter is invalid.
        """
        self._adapter = adapter

    def validate_adapter(self) -> None:
        """Validates the adapter object.

        Raises:
            RuntimeError: If the adapter is not initialized.
            TypeError: If the provided adapter is not of the expected type.
        """
        if self.adapter is None:
            msg = f"Adapter is not initialized in {self.__class__.__name__}."
            self._logger.error(msg)
            raise RuntimeError(msg)

        if not isinstance(self.adapter, Adapter):
            msg = f"Expected Adapter, got {type(self.adapter).__name__} in {self.__class__.__name__}."
            self._logger.error(msg)
            raise TypeError(msg)

    def validate_history(self) -> None:
        """Ensures the provided SessionHistory object is valid.

        Raises:
            RuntimeError: If the history object is not initialized.
            TypeError: If the provided history object is not of the expected type.
        """
        if self._session_history is None:
            msg = f"Metrics is not initialized in {self.__class__.__name__}."
            self._logger.error(msg)
            raise RuntimeError(msg)

        if not isinstance(self._session_history, SessionHistory):
            msg = f"Expected SessionHistory, got {type(self._session_history).__name__} in {self.__class__.__name__}."
            self._logger.error(msg)
            raise TypeError(msg)

    def begin_stage(self) -> None:
        """Performs stage startup processes"""
        self.validate_adapter()
        self.validate_next_stage()
        if not self._stage_clock.is_active():
            self._stage_clock.start()

    def end_stage(self) -> None:
        """Performs final steps and calls the transition method."""
        self._stage_clock.reset()
        self.transition()

    def transition(self) -> None:
        """Performs transition to the next stage if complete."""
        if isinstance(self._adapter, Adapter):
            if isinstance(self.next_stage, AdapterStage):
                self._adapter.stage = self.next_stage

    def set_baseline_statistics(self) -> None:
        """Sets baseline statistics on the adapter."""
        if isinstance(self._adapter, Adapter) and isinstance(
            self._session_history, SessionHistory
        ):
            self._adapter.baseline_snapshot = self._session_history.get_snapshot(
                time_window=self._config.duration
            )
        else:
            msg = f"Expected Adapter, got {type(self.adapter).__name__}"
            self._logger.error(msg)
            raise TypeError(msg)

    @property
    @abstractmethod
    def next_stage(self) -> Optional["AdapterStage"]:
        """AdapterStage: Returns the next stage in the sequence."""
        pass

    @next_stage.setter
    @abstractmethod
    def next_stage(self, next_stage: "AdapterStage") -> None:
        """Sets the next stage.

        Args:
            next_stage (AdapterStage): The stage to transition to.
        """
        pass

    @abstractmethod
    async def adapt(self, history: "SessionHistory") -> None:
        """Executes the adapter methods for the current stage.

        Args:
            history (SessionHistory): The current session history.
        """
        pass

    @abstractmethod
    def validate_next_stage(self) -> None:
        """Validates the next stage object."""


# ------------------------------------------------------------------------------------------------ #
#                              ADAPTER BASELINE STAGE                                              #
# ------------------------------------------------------------------------------------------------ #
class AdapterBaselineStage(AdapterStage):
    """
    Represents the baseline stage of an adapter in a session control mechanism.

    During this stage, the adapter initializes and manages session control values
    such as rate and concurrency. It also checks for valid history, adds noise to the rate,
    and transitions to the next stage when appropriate.

    Attributes:
        _rate (SessionControlValue): Manages and adjusts the rate with noise.
        _concurrency (float): Fixed concurrency level during the baseline stage.
        _duration (float): Duration of the baseline stage.
        _next_stage (Optional[AdapterRateExploreStage]): The next stage to transition to.
    """

    def __init__(self, config: Mapping[str, Union[int, float]]) -> None:
        """
        Initializes the AdapterBaselineStage with the provided configuration.

        Args:
            config (Mapping[str, Union[int, float]]): Configuration dictionary containing
                rate, min_rate, max_rate, temperature, concurrency, and duration settings.

        Initializes:
            _rate (SessionControlValue): Session control object for rate with noise adjustment.
            _concurrency (float): Concurrency value during this stage.
            _duration (float): Duration of the baseline stage.
            _next_stage (Optional[AdapterRateExploreStage]): The next stage, initially set to None.
        """
        super().__init__(config=config)

        self._rate = SessionControlValue(
            initial_value=self._config.rate,
            min_value=self._config.min_rate,
            max_value=self._config.max_rate,
            temperature=self._config.temperature,
        )

        self._concurrency: float = self._config.concurrency
        self._duration: float = self._config.duration
        self._next_stage: Optional[AdapterRateExploreStage] = None

    @property
    def next_stage(self) -> Optional[AdapterRateExploreStage]:
        """
        Gets the next stage of the adapter.

        Returns:
            Optional[AdapterRateExploreStage]: The next stage to transition to, or None if not set.
        """
        return self._next_stage

    @next_stage.setter
    def next_stage(self, next_stage: AdapterRateExploreStage) -> None:
        """
        Sets the next stage of the adapter.

        Args:
            next_stage (AdapterRateExploreStage): The stage to transition to after the baseline stage.
        """
        self._next_stage = next_stage

    async def adapt(self, history: SessionHistory) -> None:
        """
        Adjusts the session control values based on session history and transitions to the next stage if appropriate.

        This method adds noise to the rate, creates a session control object, and sets it to the adapter.
        It also checks if the stage should transition to the next one.

        Args:
            history (SessionHistory): Historical data of the session used for validation and adaptation.
        """

        # Begin the stage, setting the timer if not already set.
        self.begin_stage()
        # Save and validate history
        self._session_history = history
        # Add noise to the existing rate
        self._rate.add_noise()
        # Create a session control object for the adapter
        session_control = SessionControl(
            rate=self._rate.value, concurrency=self._concurrency
        )
        # Add the session control object to the adapter
        if isinstance(self._adapter, Adapter):
            self._adapter.session_control = session_control
        # End stage
        self.end_stage()

    def begin_stage(self) -> None:
        super().begin_stage()

    def end_stage(self) -> None:
        """
        Determines if the current stage should end and transitions to the next stage.

        Checks if the baseline stage is complete and if so, takes a snapshot of the session history
        and prepares for transition.

        Returns:
            bool: True if the stage is complete and ready for transition, False otherwise.
        """
        # Check if the stage's time has expired.
        if self._stage_clock.has_elapsed(duration=self._config.duration):
            self.set_baseline_statistics()
            self.transition()

    def transition(self) -> None:
        """
        Transitions to the next stage if the current stage has ended.

        If the baseline stage is complete and the next stage is properly set,
        this method will trigger the adapter to transition to the next stage.
        """
        if isinstance(self._adapter, Adapter) and isinstance(
            self.next_stage, AdapterRateExploreStage
        ):
            self._adapter.transition(self.next_stage)

    def validate_next_stage(self) -> None:
        """
        Validates that the next stage is correctly initialized and of the expected type.

        Raises:
            RuntimeError: If the next stage is not initialized.
            TypeError: If the next stage is not of type AdapterRateExploreStage.

        """
        if self.next_stage is None:
            msg = "Next stage is not initialized."
            self._logger.exception(msg)
            raise RuntimeError(msg)

        if not isinstance(self.next_stage, AdapterRateExploreStage):
            msg = f"Expected AdapterRateExploreStage, got {type(self.adapter).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)


# ------------------------------------------------------------------------------------------------ #
#                              ADAPTER RATE EXPLORE STAGE                                          #
# ------------------------------------------------------------------------------------------------ #
class AdapterRateExploreStage(AdapterStage):
    """
    Represents the request rate exploration stage of an adapter in a session control mechanism.

    During this stage, the adapter seeks to maximize the request rate while keeping the
    latency within baseline range. A hill-climbing algorithm repeatedly and additively increases
    the request rate. When a threshold is met, the algorithm multiplicatively decreases the rate
    until stability has returned. The process repeats for the duration of the stage, and
    the median rate observed during the stage is set for subsequent stages.

    Attributes:
        _rate (SessionControlValue): Manages and adjusts the rate with noise.
        _concurrency (float): Fixed concurrency level during the baseline stage.
        _duration (float): Duration of the baseline stage.
        _next_stage (Optional[AdapterRateExploreStage]): The next stage to transition to.
        _latency_stats (Optional[SessionStats]): Stores latency statistics for the stage.
        _latency_ave_threshold (float): Threshold for average latency used to determine stability.
        _latency_cv_threshold (float): Threshold for latency coefficient of variation.
        _step_duration (float): Duration for each step in the hill-climbing algorithm.
        _stabilization_period (bool): Indicates whether the system is in a stabilization period.
        _step_clock (Clock): Tracks time to manage stabilization periods.
    """

    def __init__(self, config: Mapping[str, Union[int, float]]) -> None:
        """
        Initializes the AdapterRateExploreStage with the provided configuration.

        Args:
            config (Mapping[str, Union[int, float]]): Configuration dictionary containing
                rate, min_rate, max_rate, temperature, concurrency, and duration settings.

        Initializes:
            _rate (SessionControlValue): Session control object for rate with noise adjustment.
            _concurrency (float): Concurrency value during this stage.
            _duration (float): Duration of the baseline stage.
            _next_stage (Optional[AdapterConcurrencyExploreStage]): The next stage, initially set to None.
            _latency_stats (Optional[SessionStats]): Latency statistics, initialized to None.
            _latency_ave_threshold (float): Latency average threshold for stability checks.
            _latency_cv_threshold (float): Latency coefficient of variation threshold.
            _step_duration (float): Duration of each rate adjustment step.
            _stabilization_period (bool): Flag to manage stabilization, starts as False.
            _step_clock (Clock): Clock instance to track stabilization periods.
        """
        super().__init__(config=config)

        # Rate control object initialized with noise management parameters.
        self._rate = SessionControlValue(
            initial_value=self._config.rate,
            min_value=self._config.min_rate,
            max_value=self._config.max_rate,
            temperature=self._config.temperature,
        )
        # Configuration of concurrency and stage duration.
        self._concurrency: float = self._config.concurrency
        self._duration: float = self._config.duration

        # Placeholder for the next stage, set later.
        self._next_stage: Optional[AdapterConcurrencyExploreStage] = None

        # Latency statistics and thresholds for stability checks.
        self._latency_stats: Optional[SessionStats] = None
        self._latency_ave_threshold: float = 0.0
        self._latency_cv_threshold: float = 0.0

        # Duration of the steps that adjust the rate.
        self._step_duration: float = self._config.step_duration

        # Stabilization flag, true when no rate changes occur.
        self._stabilization_period = False

        # Clock to manage step stabilization periods.
        self._step_clock = Clock()

    @property
    def next_stage(self) -> Optional[AdapterConcurrencyExploreStage]:
        """
        Gets the next stage of the adapter.

        Returns:
            Optional[AdapterConcurrencyExploreStage]: The next stage to transition to, or None if not set.
        """
        return self._next_stage

    @next_stage.setter
    def next_stage(self, next_stage: AdapterConcurrencyExploreStage) -> None:
        """
        Sets the next stage of the adapter.

        Args:
            next_stage (AdapterConcurrencyExploreStage): The stage to transition to after the baseline stage.
        """
        self._next_stage = next_stage

    async def adapt(self, history: SessionHistory) -> None:
        """
        Adjusts the session control values based on session history and transitions to the next stage if appropriate.

        This method adds noise to the rate, creates a session control object, and sets it to the adapter.
        It also checks if the stage should transition to the next one.

        Args:
            history (SessionHistory): Historical data of the session used for validation and adaptation.
        """
        # Start the stage and set the timer.
        self.begin_stage()

        # Save session history and validate it.
        self._session_history = history
        self.validate_history()

        # Determine whether to adapt or stabilize based on the step clock.
        if (
            self._step_clock.is_active()
            and self._step_clock.has_elapsed(self._config.step_duration)
            or not self._step_clock.is_active()
        ):
            self._adapt()
        else:
            self._stabilize()

        # Update the adapter with the current session control data.
        self._update_adapter()

        # Check if the stage should end and transition if ready.
        self.end_stage()

    def _adapt(self) -> None:
        """Conduct adaptation by adjusting the rate based on system stability."""
        if self._system_stable():
            # If the system is stable, increase the rate.
            self._rate.increase_value()
        else:
            # If the system is unstable, decrease the rate.
            self._rate.decrease_value()

    def _stabilize(self) -> None:
        """Apply noise to the rate during the stabilization period."""
        self._rate.add_noise()

    def begin_stage(self) -> None:
        """Starts the stage clock and obtains baseline latency statistics from the adapter."""
        super().begin_stage()
        if not isinstance(self._latency_stats, SessionStats):
            self._get_baseline_stats()
        if not self._stage_clock.is_active():
            self._stage_clock.start()

    def end_stage(self) -> None:
        """
        Determines if the current stage should end and transitions to the next stage.

        Checks if the baseline stage is complete and if so, takes a snapshot of the session history
        and prepares for transition.
        """
        if not self._step_clock.is_active():
            self._step_clock.start()
        if self._stage_clock.has_elapsed(duration=self._config.duration):
            self.set_baseline_statistics()
            self.transition()

    def transition(self) -> None:
        """
        Transitions to the next stage if the current stage has ended.

        If the baseline stage is complete and the next stage is properly set,
        this method will trigger the adapter to transition to the next stage.
        """
        if isinstance(self._adapter, Adapter) and isinstance(
            self.next_stage, AdapterConcurrencyExploreStage
        ):
            self._adapter.transition(self.next_stage)

    def validate_next_stage(self) -> None:
        """
        Validates that the next stage is correctly initialized and of the expected type.

        Raises:
            RuntimeError: If the next stage is not initialized.
            TypeError: If the next stage is not of type AdapterRateExploreStage.
        """
        if self.next_stage is None:
            msg = "Next stage is not initialized."
            self._logger.exception(msg)
            raise RuntimeError(msg)

        if not isinstance(self.next_stage, AdapterConcurrencyExploreStage):
            msg = f"Expected AdapterConcurrencyExploreStage, got {type(self.adapter).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)

    def _update_adapter(self) -> None:
        """Updates the session control on the adapter."""
        if isinstance(self._adapter, Adapter):
            self._adapter.session_control = SessionControl(
                rate=self._rate.median_value,
                concurrency=self._concurrency,
            )
        else:
            msg = f"Expected Adapter, got {type(self.adapter).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)

    def _system_stable(self) -> bool:
        """
        Evaluates system stability based on latency statistics.

        This method checks the latency average and coefficient of variation, and
        returns True if the values are under the thresholds set by the configuration.
        """
        if isinstance(self._session_history, SessionHistory):
            latency_stats = self._session_history.get_latency_stats(
                time_window=self._config.window_size
            )
            return (
                latency_stats.average <= self._latency_ave_threshold
                and latency_stats.cv <= self._latency_cv_threshold
            )
        else:
            msg = f"Expected SessionHistory, got {type(self._session_history).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)

    def _get_baseline_stats(self) -> None:
        """Obtains baseline latency statistics from the adapter."""
        if isinstance(self._adapter, Adapter):
            if isinstance(self._adapter.baseline_snapshot, StatisticalSnapshot):
                if isinstance(
                    self._adapter.baseline_snapshot.latency_stats, SessionStats
                ):
                    # Get the baseline latency statistics.
                    self._latency_stats = self._adapter.baseline_snapshot.latency_stats
                    # Set the latency thresholds for stability checks.
                    self._latency_ave_threshold = (
                        self._latency_stats.average * self._config.latency_multiplier
                    )
                    self._latency_cv_threshold = (
                        self._latency_stats.cv * self._config.cv_multiplier
                    )


# ------------------------------------------------------------------------------------------------ #
#                              ADAPTER CONCURRENCY EXPLORE STAGE                                   #
# ------------------------------------------------------------------------------------------------ #
class AdapterConcurrencyExploreStage(AdapterStage):
    """
    Represents the request concurrency exploration stage of an adapter in a session control mechanism.

    During this stage, the adapter seeks to maximize the concurrency while keeping the
    latency within baseline range. A hill-climbing algorithm repeatedly and additively increases
    the request currency. When a threshold is met, the algorithm multiplicatively decreases the
    concurrency until stability has returned. The process repeats for the duration of the stage,
    and the median rate observed during the stage is set for subsequent stages.

    Attributes:
        _rate (SessionControlValue): Manages and adjusts the rate with noise.
        _concurrency (float): Concurrency level during the baseline stage.
        _duration (float): Duration of the concurrency exploration stage.
        _next_stage (Optional[AdapterConcurrencyExploreStage]): The next stage to transition to.
        _latency_stats (Optional[SessionStats]): Stores latency statistics for the stage.
        _latency_ave_threshold (float): Threshold for average latency used to determine stability.
        _latency_cv_threshold (float): Threshold for latency coefficient of variation.
        _step_duration (float): Duration for each step in the hill-climbing algorithm.
        _stabilization_period (bool): Indicates whether the system is in a stabilization period.
        _step_clock (Clock): Tracks time to manage stabilization periods.
    """

    def __init__(self, config: Mapping[str, Union[int, float]]) -> None:
        """
        Initializes the AdapterConcurrencyExploreStage with the provided configuration.

        Args:
            config (Mapping[str, Union[int, float]]): Configuration dictionary containing
                rate, min_rate, max_rate, temperature, concurrency, and duration settings.

        Initializes:
            _rate (SessionControlValue): Session control object for rate with noise adjustment.
            _concurrency (float): Concurrency value during this stage.
            _duration (float): Duration of the baseline stage.
            _next_stage (Optional[AdapterConcurrencyExploreStage]): The next stage, initially set to None.
            _latency_stats (Optional[SessionStats]): Latency statistics, initialized to None.
            _latency_ave_threshold (float): Latency average threshold for stability checks.
            _latency_cv_threshold (float): Latency coefficient of variation threshold.
            _step_duration (float): Duration of each rate adjustment step.
            _stabilization_period (bool): Flag to manage stabilization, starts as False.
            _step_clock (Clock): Clock instance to track stabilization periods.
        """
        super().__init__(config=config)

        # Rate control object initialized with noise management parameters.
        self._rate = SessionControlValue(
            initial_value=self._config.rate,
            min_value=self._config.min_rate,
            max_value=self._config.max_rate,
            temperature=self._config.temperature,
        )

        # Concurrency control object.
        self._concurrency = SessionControlValue(
            initial_value=self._config.concurrency,
            min_value=self._config.min_concurrency,
            max_value=self._config.max_concurrency,
        )
        # Configuration of stage duration.
        self._duration: float = self._config.duration

        # Placeholder for the next stage, set later.
        self._next_stage: Optional[AdapterExploitStage] = None

        # Latency statistics and thresholds for stability checks.
        self._latency_stats: Optional[SessionStats] = None
        self._latency_ave_threshold: float = 0.0
        self._latency_cv_threshold: float = 0.0

        # Duration of the steps that adjust the rate.
        self._step_duration: float = self._config.step_duration

        # Stabilization flag, true when no rate changes occur.
        self._stabilization_period = False

        # Clock to manage step stabilization periods.
        self._step_clock = Clock()

    @property
    def next_stage(self) -> Optional[AdapterExploitStage]:
        """
        Gets the next stage of the adapter.

        Returns:
            Optional[AdapterExploitStage]: The next stage to transition to, or None if not set.
        """
        return self._next_stage

    @next_stage.setter
    def next_stage(self, next_stage: AdapterExploitStage) -> None:
        """
        Sets the next stage of the adapter.

        Args:
            next_stage (AdapterExploitStage): The stage to transition to after the baseline stage.
        """
        self._next_stage = next_stage

    async def adapt(self, history: SessionHistory) -> None:
        """
        Adjusts the session control values based on session history and transitions to the next stage if appropriate.

        This method adds noise to the rate, creates a session control object, and sets it to the adapter.
        It also checks if the stage should transition to the next one.

        Args:
            history (SessionHistory): Historical data of the session used for validation and adaptation.
        """
        # Start the stage and set the timer.
        self.begin_stage()

        # Save session history and validate it.
        self._session_history = history
        self.validate_history()

        # Determine whether to adapt or stabilize based on the step clock.
        if (
            self._step_clock.is_active()
            and self._step_clock.has_elapsed(self._config.step_duration)
            or not self._step_clock.is_active()
        ):
            self._adapt()
        else:
            self._stabilize()

        # Update the adapter with the current session control data.
        self._update_adapter()

        # Check if the stage should end and transition if ready.
        self.end_stage()

    def _adapt(self) -> None:
        """Conduct adaptation by adjusting the rate based on system stability."""
        if self._system_stable():
            # If the system is stable, increase the rate.
            self._concurrency.increase_value()
        else:
            # If the system is unstable, decrease the rate.
            self._concurrency.decrease_value()
        # Add noise to the rate
        self._rate.add_noise()
        # Restart the clock
        self._stage_clock.start()

    def begin_stage(self) -> None:
        """Starts the stage clock and obtains baseline latency statistics from the adapter."""
        super().begin_stage()
        if not isinstance(self._latency_stats, SessionStats):
            self._get_baseline_stats()
        if not self._stage_clock.is_active():
            self._stage_clock.start()

    def end_stage(self) -> None:
        """
        Determines if the current stage should end and transitions to the next stage.

        Checks if the baseline stage is complete and if so, takes a snapshot of the session history
        and prepares for transition.
        """
        if not self._step_clock.is_active():
            self._step_clock.start()
        if self._stage_clock.has_elapsed(duration=self._config.duration):
            self.set_baseline_statistics()
            self.transition()

    def transition(self) -> None:
        """
        Transitions to the next stage if the current stage has ended.

        If the baseline stage is complete and the next stage is properly set,
        this method will trigger the adapter to transition to the next stage.
        """
        if isinstance(self._adapter, Adapter) and isinstance(
            self.next_stage, AdapterConcurrencyExploreStage
        ):
            self._adapter.transition(self.next_stage)

    def validate_next_stage(self) -> None:
        """
        Validates that the next stage is correctly initialized and of the expected type.

        Raises:
            RuntimeError: If the next stage is not initialized.
            TypeError: If the next stage is not of type AdapterConcurrencyExploreStage.
        """
        if self.next_stage is None:
            msg = "Next stage is not initialized."
            self._logger.exception(msg)
            raise RuntimeError(msg)

        if not isinstance(self.next_stage, AdapterConcurrencyExploreStage):
            msg = f"Expected AdapterConcurrencyExploreStage, got {type(self.adapter).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)

    def _stabilize(self) -> None:
        """Apply noise to the rate during the stabilization period."""
        self._rate.add_noise()

    def _update_adapter(self) -> None:
        """Updates the session control on the adapter."""
        if isinstance(self._adapter, Adapter):
            self._adapter.session_control = SessionControl(
                rate=self._rate.median_value,
                concurrency=self._concurrency.value,
            )
        else:
            msg = f"Expected Adapter, got {type(self.adapter).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)

    def _system_stable(self) -> bool:
        """
        Evaluates system stability based on latency statistics.

        This method checks the latency average and coefficient of variation, and
        returns True if the values are under the thresholds set by the configuration.
        """
        if isinstance(self._session_history, SessionHistory):
            latency_stats = self._session_history.get_latency_stats(
                time_window=self._config.window_size
            )
            return (
                latency_stats.average <= self._latency_ave_threshold
                and latency_stats.cv <= self._latency_cv_threshold
            )
        else:
            msg = f"Expected SessionHistory, got {type(self._session_history).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)

    def _get_baseline_stats(self) -> None:
        """Obtains baseline latency statistics from the adapter."""
        if isinstance(self._adapter, Adapter):
            if isinstance(self._adapter.baseline_snapshot, StatisticalSnapshot):
                if isinstance(
                    self._adapter.baseline_snapshot.latency_stats, SessionStats
                ):
                    # Get the baseline latency statistics.
                    self._latency_stats = self._adapter.baseline_snapshot.latency_stats
                    # Set the latency thresholds for stability checks.
                    self._latency_ave_threshold = (
                        self._latency_stats.average * self._config.latency_multiplier
                    )
                    self._latency_cv_threshold = (
                        self._latency_stats.cv * self._config.cv_multiplier
                    )


# ------------------------------------------------------------------------------------------------ #
#                                ADAPTER EXPLOIT STAGE                                             #
# ------------------------------------------------------------------------------------------------ #
class AdapterExploitStage(AdapterStage):
    """
    Represents the exploitation stage where concurrency is fixed at the previous stage
    level and rate is adjusted based upon changes in latency average and the variation.

    Attributes:
        _rate (SessionControlValue): Manages and adjusts the rate with noise.
        _concurrency (float): Fixed concurrency level during the baseline stage.
        _duration (float): Duration of the exploitation stage.
        _next_stage (Optional[AdapterRateBaselineStage]): The next stage to transition to.
        _latency_stats (Optional[SessionStats]): Stores latency statistics for the stage.
        _latency_ave_threshold (float): Threshold for average latency used to determine stability.
        _latency_cv_threshold (float): Threshold for latency coefficient of variation.
        _step_duration (float): Duration for each step in the hill-climbing algorithm.
        _stabilization_period (bool): Indicates whether the system is in a stabilization period.
        _step_clock (Clock): Tracks time to manage stabilization periods.
    """

    def __init__(self, config: Mapping[str, Union[int, float]]) -> None:
        """
        Initializes the AdapterExploitStage with the provided configuration.

        Args:
            config (Mapping[str, Union[int, float]]): Configuration dictionary containing
                rate, min_rate, max_rate, temperature, concurrency, and duration settings.

        Initializes:
            _rate (SessionControlValue): Session control object for rate with noise adjustment.
            _concurrency (float): Concurrency value during this stage.
            _duration (float): Duration of the baseline stage.
            _next_stage (Optional[AdapterExploitStage]): The next stage, initially set to None.
            _latency_stats (Optional[SessionStats]): Latency statistics, initialized to None.
            _latency_ave_threshold (float): Latency average threshold for stability checks.
            _latency_cv_threshold (float): Latency coefficient of variation threshold.
            _step_duration (float): Duration of each rate adjustment step.
            - k (float): Sensitivity parameter for latency adjustments.
            - m (float): Sensitivity parameter for CV adjustments.
            _step_clock (Clock): Clock instance to track stabilization periods.
        """
        super().__init__(config=config)

        # Rate
        self._rate: float = 0.0
        # Concurrency
        self._concurrency: float = 0.0
        # Configuration of stage duration.
        self._duration: float = self._config.duration

        # Parameters for rate adjustment
        self._k = self._config.k
        self._m = self._config.m

        # Placeholder for the next stage, set later.
        self._next_stage: Optional[AdapterExploitStage] = None

        # Latency statistics and thresholds for stability checks.
        self._latency_stats: Optional[SessionStats] = None
        self._latency_ave_threshold: float = 0.0
        self._latency_cv_threshold: float = 0.0

        # Duration of the steps that adjust the rate.
        self._step_duration: float = self._config.step_duration

        # Stabilization flag, true when no rate changes occur.
        self._stabilization_period = False

        # Clock to manage step stabilization periods.
        self._step_clock = Clock()

    @property
    def next_stage(self) -> Optional[AdapterExploitStage]:
        """
        Gets the next stage of the adapter.

        Returns:
            Optional[AdapterExploitStage]: The next stage to transition to, or None if not set.
        """
        return self._next_stage

    @next_stage.setter
    def next_stage(self, next_stage: AdapterExploitStage) -> None:
        """
        Sets the next stage of the adapter.

        Args:
            next_stage (AdapterExploitStage): The stage to transition to after the baseline stage.
        """
        self._next_stage = next_stage

    async def adapt(self, history: SessionHistory) -> None:
        """
        Adjusts the session control values based on session history and transitions to the next stage if appropriate.

        This method adds noise to the rate, creates a session control object, and sets it to the adapter.
        It also checks if the stage should transition to the next one.

        Args:
            history (SessionHistory): Historical data of the session used for validation and adaptation.
        """
        # Start the stage and set the timer.
        self.begin_stage()

        # Save session history and validate it.
        self._session_history = history
        self.validate_history()

        self._adapt()

        # Update the adapter with the current session control data.
        self._update_adapter()

        # Check if the stage should end and transition if ready.
        self.end_stage()

    def _adapt(self) -> None:
        """Conduct adaptation by adjusting the rate based on system stability."""
        # Get current statistics
        if isinstance(self._session_history, SessionHistory):
            latency_stats = self._session_history.get_latency_stats(
                time_window=self._config.window_size
            )
        latency_mean = latency_stats.average
        latency_cv = latency_stats.cv
        # Compute Latency and CV Ratio
        if isinstance(self._latency_stats, SessionStats):
            latency_ratio = latency_mean / self._latency_stats.average
            cv_ratio = latency_cv / self._latency_stats.cv
        # Compute new request rate
        self._rate = (
            self._rate
            * (1 - self._k * (latency_ratio - 1))
            * (1 - self._m * (cv_ratio - 1))
        )

    def begin_stage(self) -> None:
        """Starts the stage clock and obtains baseline latency statistics from the adapter."""
        super().begin_stage()
        if not isinstance(self._latency_stats, SessionStats):
            self._get_baseline_stats()
        if not self._stage_clock.is_active():
            self._stage_clock.start()
        self._get_current_rate()

    def end_stage(self) -> None:
        """
        Determines if the current stage should end and transitions to the next stage.

        Checks if the baseline stage is complete and if so, takes a snapshot of the session history
        and prepares for transition.
        """
        if not self._step_clock.is_active():
            self._step_clock.start()
        if self._stage_clock.has_elapsed(duration=self._config.duration):
            self.transition()

    def transition(self) -> None:
        """
        Transitions to the next stage if the current stage has ended.

        If the baseline stage is complete and the next stage is properly set,
        this method will trigger the adapter to transition to the next stage.
        """
        if isinstance(self._adapter, Adapter) and isinstance(
            self.next_stage, AdapterExploitStage
        ):
            self._adapter.transition(self.next_stage)

    def validate_next_stage(self) -> None:
        """
        Validates that the next stage is correctly initialized and of the expected type.

        Raises:
            RuntimeError: If the next stage is not initialized.
            TypeError: If the next stage is not of type AdapterExploitStage.
        """
        if self.next_stage is None:
            msg = "Next stage is not initialized."
            self._logger.exception(msg)
            raise RuntimeError(msg)

        if not isinstance(self.next_stage, AdapterExploitStage):
            msg = f"Expected AdapterExploitStage, got {type(self.adapter).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)

    def _update_adapter(self) -> None:
        """Updates the session control on the adapter."""
        if isinstance(self._adapter, Adapter):
            self._adapter.session_control = SessionControl(
                rate=self._rate,
                concurrency=self._adapter.session_control.concurrency,
            )
        else:
            msg = f"Expected Adapter, got {type(self.adapter).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)

    def _system_stable(self) -> bool:
        """
        Evaluates system stability based on latency statistics.

        This method checks the latency average and coefficient of variation, and
        returns True if the values are under the thresholds set by the configuration.
        """
        if isinstance(self._session_history, SessionHistory):
            latency_stats = self._session_history.get_latency_stats(
                time_window=self._config.window_size
            )
            return (
                latency_stats.average <= self._latency_ave_threshold
                and latency_stats.cv <= self._latency_cv_threshold
            )
        else:
            msg = f"Expected SessionHistory, got {type(self._session_history).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)

    def _get_current_rate(self) -> None:
        """Obtains the current rate from the adapter"""
        if isinstance(self._adapter, Adapter):
            if isinstance(self._adapter.session_control, SessionControl):
                self._rank = self._adapter.session_control.rate

    def _get_baseline_stats(self) -> None:
        """Obtains baseline latency statistics from the adapter."""
        if isinstance(self._adapter, Adapter):
            if isinstance(self._adapter.baseline_snapshot, StatisticalSnapshot):
                if isinstance(
                    self._adapter.baseline_snapshot.latency_stats, SessionStats
                ):
                    # Get the baseline latency statistics.
                    self._latency_stats = self._adapter.baseline_snapshot.latency_stats
