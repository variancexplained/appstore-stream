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
# Modified   : Friday August 23rd 2024 05:51:40 am                                                 #
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
        self._stage_timestamp: float = 0.0
        self._stage_active = False
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
        if not self._stage_active:
            self._stage_timestamp = time.time()
            self._stage_active = True

    def end_stage(self) -> None:
        """Performs final steps and calls the transition method."""
        self.transition()

    def transition(self) -> None:
        """Performs transition to the next stage if complete."""
        if isinstance(self._adapter, Adapter):
            if isinstance(self.next_stage, AdapterStage):
                self._adapter.stage = self.next_stage

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

    def end_stage(self) -> None:
        """
        Determines if the current stage should end and transitions to the next stage.

        Checks if the baseline stage is complete and if so, takes a snapshot of the session history
        and prepares for transition.

        Returns:
            bool: True if the stage is complete and ready for transition, False otherwise.
        """
        # Check if the stage's time has expired.
        elapsed_time = time.time() - self._stage_timestamp
        if elapsed_time > self._config.duration:
            # Get baseline statistics and set them on the adapter object.
            if isinstance(self._adapter, Adapter) and isinstance(
                self._session_history, SessionHistory
            ):
                self._adapter.baseline_snapshot = self._session_history.get_snapshot(
                    time_window=self._config.duration
                )
                self.transition()
            else:
                msg = f"Expected Adapter, got {type(self.adapter).__name__}"
                self._logger.error(msg)
                raise TypeError(msg)

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
    Represents the request rate exploration stage  of an adapter in a session control mechanism.

    During this stage, the adapter seeks to maximize the request rate while keeping the
    latency within baseline range. A hillclimbing algorithm repeated additively increases
    the request. When a threshold is met, the algorithm multiplicatively decreases the rate
    until stability has returned. The process repeats for the duration of the stage and
    the median rate observed during the stage is set for subsequent stages.

    Attributes:
        _rate (SessionControlValue): Manages and adjusts the rate with noise.
        _concurrency (float): Fixed concurrency level during the baseline stage.
        _duration (float): Duration of the baseline stage.
        _next_stage (Optional[AdapterRateExploreStage]): The next stage to transition to.
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
            _next_stage (Optional[AdapterRateExploreStage]): The next stage, initially set to None.
        """
        super().__init__(config=config)

        # Rate control object.
        self._rate = SessionControlValue(
            initial_value=self._config.rate,
            min_value=self._config.min_rate,
            max_value=self._config.max_rate,
            temperature=self._config.temperature,
        )
        # Configuration of the stage
        self._concurrency: float = self._config.concurrency
        self._duration: float = self._config.duration
        # The next stage is AdaptConcurrencyExploreStage
        self._next_stage: Optional[AdapterConcurrencyExploreStage] = None
        # Latency statistics.
        self._latency_stats: Optional[SessionStats] = None
        self._latency_ave_threshold: float = 0.0
        self._latency_cv_threshold: float = 0.0
        # Duration of the steps that adjust the rate and timestamp
        self._step_duration: float = self._config.step_duration
        # During the stabilization period, no changes to rate occur.
        self._stabilization_period = False
        # Timestamp for the stabilization period.
        self._step_timestamp: float = 0

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
        # Begin the stage, set the timer and lets go.
        self.begin_stage()

        # Save and validate history
        self._session_history = history
        # If invalid, an exception will be raised. No need to
        self.validate_history()
        # If in stabilization period, we add noise to the current rate and return
        if self._stabilizing:
            self._rate.add_noise()
        else:
            # Check performance of the system
            if self._system_stable():
                self._rate.increase_value()
            else:
                self._rate.decrease_value()
        # Create a session control object
        session_control = SessionControl(
            rate=self._rate.value, concurrency=self._concurrency
        )
        # Add the session control object to the adapter
        if isinstance(self._adapter, Adapter):
            self._adapter.session_control = session_control

        # Check for transition
        self.end_stage()

    def begin_step(self) -> None:
        """Starts the step timer"""
        self._step_timestamp = time.time()
        self._stabilization_period = True

    def begin_stage(self) -> None:
        """Sets the timeer and obtains baseline latency stats from the adapter."""
        # Set the timer.
        super().begin_stage()
        # Check for baseline stats
        if not isinstance(self._latency_stats, SessionStats):
            self._get_baseline_stats()
            self._stabilization_period = False

    def end_stage(self) -> None:
        """
        Determines if the current stage should end and transitions to the next stage.

        Checks if the baseline stage is complete and if so, takes a snapshot of the session history
        and prepares for transition.

        Returns:
            bool: True if the stage is complete and ready for transition, False otherwise.
        """
        # Check if the stage's time has expired.
        elapsed_time = time.time() - self._stage_timestamp
        if elapsed_time > self._config.duration:

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
        """Updates the session control on the adapter"""
        # Static type checking because...
        if isinstance(self._adapter, Adapter):
            # Create a session control object with the median rate
            # Encountered during the stage.
            self._adapter.session_control = SessionControl(
                rate=self._rate.median_value,
                concurrency=self._concurrency,
            )
        else:
            msg = f"Expected Addpter, got {type(self.adapter).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)

    def _system_stable(self) -> bool:
        """Evaluates system stability based on latency.

        This method checks the latency average and coefficient of variation and
        returns True if the values are under a threshold set by configuration.
        """
        if isinstance(self._session_history, SessionHistory):
            latency_stats = self._session_history.get_latency_stats(
                time_window=self._config.window_size
            )
            if (
                latency_stats.average > self._latency_ave_threshold
                or latency_stats.cv > self._latency_cv_threshold
            ):
                return False
            else:
                return True
        else:
            msg = f"Expected SessionHistory, got {type(self._session_history).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)

    def _get_baseline_stats(self) -> None:
        """Obtains baseline stats from the adapter."""
        # Series of annoying static type checks for mypy
        if isinstance(self._adapter, Adapter):
            if isinstance(self._adapter.baseline_snapshot, StatisticalSnapshot):
                if isinstance(
                    self._adapter.baseline_snapshot.latency_stats, SessionStats
                ):
                    # Obtain baseline statistics from the adapter.
                    self._latency_stats = self._adapter.baseline_snapshot.latency_stats
                    # Compute the latency average threshold
                    self._latency_ave_threshold = (
                        self._latency_stats.average * self._config.threshold
                    )
                    # Compute the latency coefficient of variation threshold.
                    self._latency_cv_threshold = (
                        self._latency_stats.cv * self._config.threshold
                    )
                else:
                    msg = f"Expected SessionStats, got {type(self._adapter.baseline_snapshot.latency_stats).__name__} in {self.__class__.__name__}."
                    self._logger.exception(msg)
                    raise RuntimeError(msg)
            else:
                msg = f"Expected StatisticalSnapshot, got {type(self._adapter.baseline_snapshot).__name__} in {self.__class__.__name__}."
                self._logger.exception(msg)
                raise RuntimeError(msg)
        else:
            msg = f"Adapter, got {type(self._adapter).__name__} in {self.__class__.__name__}."
            self._logger.exception(msg)
            raise RuntimeError(msg)

    def _stabilizing(self) -> bool:
        """Returns True if Step has expired."""
        if self._stabilization_period:
            elapsed_time = time.time() - self._step_timestamp
            return elapsed_time < self._step_duration
        else:
            return False

    def _stage_expired(self) -> bool:
        """Returns True if Stage has expired."""
        elapsed_time = time.time() - self._stage_timestamp
        return elapsed_time > self._config.duration


# ------------------------------------------------------------------------------------------------ #
#                         ADAPTER CONCURRENCY EXPLORE STAGE                                        #
# ------------------------------------------------------------------------------------------------ #
class AdapterConcurrencyExploreStage(AdapterStage):
    """
    Represents the request concurrency exploration stage  of an adapter in a session control mechanism.

    During this stage, the adapter seeks to maximize throughput while keeping the
    latency within baseline range. A hillclimbing algorithm repeated additively increases
    the concurrency. When a threshold is met, the algorithm multiplicatively decreases the concurrency
    until stability has returned. The process repeats for the duration of the stage and
    the median concurrency observed during the stage is set for subsequent stages.

    Attributes:
        _rate (SessionControlValue): Manages and adjusts the rate with noise.
        _concurrency (float): Concurrency value adjusted during this stage
        _duration (float): Duration of the baseline stage.
        _next_stage (Optional[AdapterExploitStage]): The next stage to which we transition
    """

    def __init__(self, config: Mapping[str, Union[int, float]]) -> None:
        """
        Initializes the AdapterConcurrencyExploreStage with the provided configuration.

        Args:
            config (Mapping[str, Union[int, float]]): Configuration dictionary containing
                concurrency, min_concurrency, max_concurrency, temperature, concurrency, and duration settings.

        Initializes:
            _rate (SessionControlValue): Session control object for rate with noise adjustment.
            _concurrency (float): Concurrency value during this stage.
            _duration (float): Duration of the baseline stage.
            _next_stage (Optional[AdapterConcurrencyExploreStage]): The next stage, initially set to None.
        """
        super().__init__(config=config)

        # Rate Control object
        self._rate = SessionControlValue(
            initial_value=self._adapter.session_control.rate,
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
        # Stage durataion
        self._duration: float = self._config.duration
        # The next stage is AdaptConcurrencyExploreStage
        self._next_stage: Optional[AdapterExploitStage] = None
        # Latency statistics.
        self._latency_stats: Optional[SessionStats] = None
        self._latency_ave_threshold: float = 0.0
        self._latency_cv_threshold: float = 0.0
        # Throughput stats
        self._throughput_stats: Optional[SessionStats] = None
        self._max_throughput: float = 0
        # Duration of the steps that adjust the concurrency and timestamp
        self._step_duration: float = self._config.step_duration
        # During the stabilization period, no changes to concurrency occur.
        self._stabilization_period = False
        # Timestamp for the stabilization period.
        self._step_timestamp: float = 0

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

        This method adds noise to the concurrency, creates a session control object, and sets it to the adapter.
        It also checks if the stage should transition to the next one.

        Args:
            history (SessionHistory): Historical data of the session used for validation and adaptation.
        """
        # Begin the stage, set the timer and lets go.
        self.begin_stage()

        # Save and validate history
        self._session_history = history
        # If invalid, an exception will be raised. No need to
        self.validate_history()
        # If in stabilization period, we add noise to the current concurrency and return
        if self._stabilization_period:
            self._concurrency.add_noise()
        else:
            # Check performance of the system
            if self._system_stable():
                self._concurrency.increase_value()
            else:
                self._concurrency.decrease_value()
        # Create a session control object
        session_control = SessionControl(
            concurrency=self._concurrency.value, concurrency=self._concurrency
        )
        # Add the session control object to the adapter
        if isinstance(self._adapter, Adapter):
            self._adapter.session_control = session_control

        # Check for transition
        self.end_stage()

    def begin_step(self) -> None:
        """Starts the step timer"""
        self._step_timestamp = time.time()

    def begin_stage(self) -> None:
        """Sets the timeer and obtains baseline latency stats from the adapter."""
        # Set the timer.
        super().begin_stage()
        # Check for baseline stats
        if not isinstance(self._latency_stats, SessionStats):
            self._get_baseline_stats()
            self._stabilization_period = False

    def _get_baseline_stats(self) -> None:
        """Obtains baseline stats from the adapter."""
        # Series of annoying static type checks for mypy
        if isinstance(self._adapter, Adapter):
            if isinstance(self._adapter.baseline_snapshot, StatisticalSnapshot):
                if isinstance(
                    self._adapter.baseline_snapshot.latency_stats, SessionStats
                ):
                    # Obtain baseline statistics from the adapter.
                    self._latency_stats = self._adapter.baseline_snapshot.latency_stats
                    # Compute the latency average threshold
                    self._latency_ave_threshold = (
                        self._latency_stats.average * self._config.threshold
                    )
                    # Compute the latency coefficient of variation threshold.
                    self._latency_cv_threshold = (
                        self._latency_stats.cv * self._config.threshold
                    )
                else:
                    msg = f"Expected SessionStats, got {type(self._adapter.baseline_snapshot.latency_stats).__name__} in {self.__class__.__name__}."
                    self._logger.exception(msg)
                    raise RuntimeError(msg)
            else:
                msg = f"Expected StatisticalSnapshot, got {type(self._adapter.baseline_snapshot).__name__} in {self.__class__.__name__}."
                self._logger.exception(msg)
                raise RuntimeError(msg)
        else:
            msg = f"Adapter, got {type(self._adapter).__name__} in {self.__class__.__name__}."
            self._logger.exception(msg)
            raise RuntimeError(msg)

    def end_stage(self) -> None:
        """
        Determines if the current stage should end and transitions to the next stage.

        Checks if the baseline stage is complete and if so, takes a snapshot of the session history
        and prepares for transition.

        Returns:
            bool: True if the stage is complete and ready for transition, False otherwise.
        """
        # Check if the stage's time has expired.
        elapsed_time = time.time() - self._stage_timestamp
        if elapsed_time > self._config.duration:
            # Static type checking because...
            if isinstance(self._adapter, Adapter):
                # Create a session control object with the median concurrency
                # Encountered during the stage.
                self._adapter.session_control = SessionControl(
                    concurrency=self._concurrency.median_value,
                    concurrency=self._concurrency,
                )
            else:
                msg = f"Expected Addpter, got {type(self.adapter).__name__}"
                self._logger.exception(msg)
                raise TypeError(msg)

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

    def _system_stable(self) -> bool:
        """Evaluates system stability based on latency.

        This method checks the latency average and coefficient of variation and
        returns True if the values are under a threshold set by configuration.
        """
        if isinstance(self._session_history, SessionHistory):
            latency_stats = self._session_history.get_latency_stats(
                time_window=self._config.window_size
            )
            if (
                latency_stats.average > self._latency_ave_threshold
                or latency_stats.cv > self._latency_cv_threshold
            ):
                return False
            else:
                return True
        else:
            msg = f"Expected SessionHistory, got {type(self._session_history).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)
