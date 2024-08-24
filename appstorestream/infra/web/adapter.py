#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/web/adapter.py                                                #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 04:44:47 am                                                   #
# Modified   : Saturday August 24th 2024 05:48:59 am                                               #
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
from typing import Optional

import numpy as np
from dependency_injector.providers import ConfigurationOption

from appstorestream.core.data import NestedNamespace
from appstorestream.infra.web.profile import (
    SessionControl,
    SessionHistory,
    SessionStats,
    StatisticalSnapshot,
)


# ------------------------------------------------------------------------------------------------ #
#                                        CLOCK                                                     #
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
        self._snapshot: Optional[StatisticalSnapshot] = None
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
    def snapshot(self) -> Optional[StatisticalSnapshot]:
        return self._snapshot

    @snapshot.setter
    def snapshot(self, snapshot: StatisticalSnapshot) -> None:
        self._snapshot = snapshot

    def adapt(self, history: SessionHistory) -> None:
        """Computes the adapted value and sets the appropriate property."""
        self._stage.adapt(history=history)

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
        config (ConfigurationOption): Configuration parameters for the stage.

    Attributes:
        _config (NestedNamespace): A nested namespace object containing the configuration parameters.
        rate (float): The current rate, default is 50.
        concurrency (float): The current concurrency, default is 50.
        adapter (Optional[Adapter]): The current adapter associated with the stage, initially None.
        _logger (logging.Logger): Logger instance for the class.
    """

    def __init__(self, config: ConfigurationOption) -> None:
        self._config = NestedNamespace(dictionary=dict(config))
        self._adapter: Optional[Adapter] = None
        self._session_history: Optional[SessionHistory] = None
        self._stage_clock = Clock()

        self._logger = logging.getLogger(f"{self.__class__.__name__}")

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

    def adapt(self, history: "SessionHistory") -> None:
        """Executes the adapter methods for the current stage.

        Args:
            history (SessionHistory): The current session history.
        """
        # Begin the stage by validating the history object and initializing the clock
        self.begin_session(history=history)
        # Perform stage specific logic
        session_control = self.execute_session()
        # Wrap up the stage, and update the adapter object, and transition as appropriate.
        self.end_session(session_control=session_control)

    def begin_stage(self) -> None:
        self._stage_clock.start()
        self.initialize_session_control()

    def initialize_session_control(self) -> None:
        """Initializes rate and concurrency for the stage."""
        self._rate = SessionControlValue(
            initial_value=float(self._config.rate),
            min_value=float(self._config.min_rate),
            max_value=float(self._config.max_rate),
            temperature=float(self._config.temperature),
        )
        self._concurrency = SessionControlValue(
            initial_value=float(self._config.concurrency),
            min_value=float(self._config.min_concurrency),
            max_value=float(self._config.max_concurrency),
        )

    def begin_session(self, history: SessionHistory) -> None:
        """Performs stage startup processes"""
        self._history = history
        self._validate_history()
        self._validate_adapter()
        self._validate_next_stage()
        if not self._stage_clock.is_active():
            self.begin_stage()

    @abstractmethod
    def execute_session(self) -> SessionControl:
        """Performs the core logic of the stage."""

    def end_session(self, session_control: SessionControl) -> None:
        # Update the Adapter with rate and concurrency
        if isinstance(self._adapter, Adapter):
            self._adapter.session_control = session_control
        # Check for transition
        if self._stage_clock.has_elapsed(duration=float(self._config.duration)):
            self.end_stage()

    def end_stage(self) -> None:
        """Performs final steps and calls the transition method."""
        # Add the session control object to the adapter
        self._stage_clock.reset()
        self._take_snapshot()
        self.transition()

    def _take_snapshot(self) -> None:
        """Sets baseline statistics on the adapter."""
        if isinstance(self._adapter, Adapter) and isinstance(
            self._session_history, SessionHistory
        ):
            self._adapter.snapshot = self._session_history.get_snapshot(
                time_window=int(self._config.window_size)
            )

    @abstractmethod
    def transition(self) -> None:
        """Performs transition to the next stage if complete."""

    @abstractmethod
    def _validate_next_stage(self) -> None:
        """Validates the next stage object."""

    def _validate_adapter(self) -> None:
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

    def _validate_history(self) -> None:
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

    def __init__(self, config: ConfigurationOption) -> None:
        """
        Initializes the AdapterBaselineStage with the provided configuration.

        Args:
            config (ConfigurationOption): Configuration dictionary containing
                rate, min_rate, max_rate, temperature, concurrency, and duration settings.

        Initializes:
            _rate (SessionControlValue): Session control object for rate with noise adjustment.
            _concurrency (float): Concurrency value during this stage.
            _duration (float): Duration of the baseline stage.
            _next_stage (Optional[AdapterRateExploreStage]): The next stage, initially set to None.
        """
        super().__init__(config=config)

        # Default Rate. Overriden in initialize concurrency
        self._rate = SessionControlValue(
            initial_value=float(self._config.rate),
            min_value=float(self._config.min_rate),
            max_value=float(self._config.max_rate),
            temperature=float(self._config.temperature),
        )

        # Default Concurrency. Overriden in initialize concurrency
        self._concurrency = SessionControlValue(
            initial_value=float(self._config.concurrency),
            min_value=float(self._config.min_concurrency),
            max_value=float(self._config.max_concurrency),
        )
        self._duration: float = float(self._config.duration)
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

    def begin_stage(self) -> None:
        super().begin_stage()

    def initialize_session_control(self) -> None:
        super().initialize_session_control()

    def begin_session(self, history: SessionHistory) -> None:
        super().begin_session(history=history)

    def execute_session(self) -> SessionControl:
        """
        Adjusts the session control values based on session history and transitions to the next stage if appropriate.

        This method adds noise to the rate, creates a session control object, and sets it to the adapter.
        It also checks if the stage should transition to the next one.

        Args:
            history (SessionHistory): Historical data of the session used for validation and adaptation.
        """

        self._rate.add_noise()
        # Create a session control object for the adapter
        return SessionControl(
            rate=self._rate.value, concurrency=self._concurrency.value
        )

    def end_session(self, session_control: SessionControl) -> None:
        """
        Determines if the current stage should end and transitions to the next stage.

        Checks if the baseline stage is complete and if so, takes a snapshot of the session history
        and prepares for transition.

        Returns:
            bool: True if the stage is complete and ready for transition, False otherwise.
        """
        super().end_session(session_control=session_control)

    def end_stage(self) -> None:
        super().end_stage()

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

    def _validate_next_stage(self) -> None:
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
    pass


# ------------------------------------------------------------------------------------------------ #
#                              ADAPTER CONCURRENCY EXPLORE STAGE                                   #
# ------------------------------------------------------------------------------------------------ #
class AdapterConcurrencyExploreStage(AdapterStage):
    pass


# ------------------------------------------------------------------------------------------------ #
#                                ADAPTER EXPLOIT STAGE                                             #
# ------------------------------------------------------------------------------------------------ #
class AdapterExploitStage(AdapterStage):
    pass
