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
# Modified   : Saturday August 24th 2024 06:17:59 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Autothrottle Module"""
from __future__ import annotations

import logging
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
        """Returns the time elapsed since the clock was started."""
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
        initial_value: float = 50.0,
        min_value: float = 50.0,
        max_value: float = 500.0,
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
        # Logging object for the class.
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def value(self) -> float:
        """Get the current value.

        Returns:
            float: The current adaptive value.
        """
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = value

    def increase_value(self, noise: bool = True) -> None:
        """Increase the value additively, respecting min/max constraints.

        The current value is increased by the additive factor plus noise,
        and if the resulting value exceeds the maximum allowable value,
        it is set to the maximum value.
        """
        prior_value = self._value
        new_value = self._value + self._additive_factor
        if noise:
            new_value += np.random.normal(loc=0, scale=self._temperature)
        self._value = min(new_value, self._max_value)

    def decrease_value(self, noise: bool = True) -> None:
        """Decrease the value multiplicatively, respecting min/max constraints.

        The current value is multiplied by the multiplicative factor plus noise,
        and if the resulting value falls below the minimum allowable value,
        it is set to the minimum value.
        """
        prior_value = self._value
        new_value = self._value * self._multiplicative_factor
        if noise:
            new_value += np.random.normal(loc=0, scale=self._temperature)
        self._value = max(new_value, self._min_value)

    def reset_value(self) -> None:
        """Reset value to the initial value.

        This method restores the adaptive value to its initial value as set
        during the initialization of the mixin.
        """
        self._value = self._initial_value

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
        self._session_history: SessionHistory = SessionHistory()
        self._session_control: SessionControl = SessionControl()
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.transition(stage=initial_stage)

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

    def adapt(self, history: SessionHistory) -> None:
        """Computes the adapted value and sets the appropriate property."""
        self._session_history = history
        self._stage.adapt()

    def transition(self, stage: AdapterStage) -> None:
        self._logger.info(
            f"{self.__class__.__name__} transitioning to {stage.__class__.__name__}"
        )
        self._stage = stage
        self._stage.adapter = self

    def get_latency_stats(self, time_window: Optional[int] = None) -> SessionStats:
        return self._session_history.get_latency_stats(time_window=time_window)

    def get_snapshot(self, time_window: Optional[int] = None) -> StatisticalSnapshot:
        return self._session_history.get_snapshot(time_window=time_window)


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
        self._stage_clock = Clock()

        # Default Rate and Concurrency Values.
        self._rate = SessionControlValue(
            initial_value=float(self._config.rate.base),
            min_value=float(self._config.rate.min),
            max_value=float(self._config.rate.max),
            temperature=float(self._config.temperature),
        )
        self._concurrency = SessionControlValue(
            initial_value=float(self._config.concurrency.base),
            min_value=float(self._config.concurrency.min),
            max_value=float(self._config.concurrency.max),
            temperature=float(self._config.temperature),
        )

        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

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

    def adapt(self) -> None:
        """Executes the adapter methods for the current stage.

        Args:
            history (SessionHistory): The current session history.
        """
        # Begin the stage by validating the history object and initializing the clock
        self.begin_session()
        # Perform stage specific logic
        session_control = self.execute_session()
        # Wrap up the stage, and update the adapter object, and transition as appropriate.
        self.end_session(session_control=session_control)

    def begin_stage(self) -> None:
        self._stage_clock.start()
        self.initialize_session_control()

    def initialize_session_control(self) -> None:
        """Method available for subclasses that must override the default session control."""
        pass

    def begin_session(self) -> None:
        """Performs stage startup processes"""
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
        self.transition()

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

    def begin_session(self) -> None:
        super().begin_session()

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
            msg = f"Next stage is not initialized in {self.__class__.__name__}."
            self._logger.exception(msg)
            raise RuntimeError(msg)

        if not isinstance(self.next_stage, AdapterRateExploreStage):
            msg = f"Expected AdapterRateExploreStage, got {type(self.next_stage).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)


# ------------------------------------------------------------------------------------------------ #
#                            ADAPTER EXPLORE EXPLOIT STAGE                                         #
# ------------------------------------------------------------------------------------------------ #
class AdapterExploreExploitStage(AdapterStage):
    """Abstract base class for stages that explore values of rate and concurrency"""

    def __init__(self, config: ConfigurationOption) -> None:
        super().__init__(config=config)

        # Latency statistics and thresholds for stability checks.
        self._baseline_latency_stats = SessionStats()
        self._baseline_latency_ave_threshold: float = 0.0
        self._baseline_latency_cv_threshold: float = 0.0
        # Step clock that monitors stabilization periods.
        self._step_clock = Clock()

        self._stabilization_period: bool = False

        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def adapt(self) -> None:
        super().adapt()

    def begin_stage(self) -> None:
        super().begin_stage()
        self.set_baseline_latency_stats()

    def initialize_session_control(self) -> None:
        super().initialize_session_control()

    def begin_session(self) -> None:
        super().begin_session()

    def end_session(self, session_control: SessionControl) -> None:
        super().end_session(session_control=session_control)

    def end_stage(self) -> None:
        super().end_stage()

    def system_stable(self) -> bool:
        """
        Evaluates system stability based on latency statistics.

        This method checks the latency average and coefficient of variation, and
        returns True if the values are under the thresholds set by the configuration.
        """
        current_latency_stats = self.get_current_latency_stats()

        # Set the latency thresholds for stability checks.
        self._baseline_latency_ave_threshold = (
            self._baseline_latency_stats.average * self._config.threshold
        )
        self._baseline_latency_cv_threshold = (
            self._baseline_latency_stats.cv * self._config.threshold
        )

        stable = (
            current_latency_stats.average <= self._baseline_latency_ave_threshold
            and current_latency_stats.cv <= self._baseline_latency_cv_threshold
        )

        # Compute percent of baseline stats for logging.
        latency_ave_pct = (
            (current_latency_stats.average - self._baseline_latency_ave_threshold)
            / self._baseline_latency_ave_threshold
        ) * 100
        latency_cv_pct = (
            (current_latency_stats.cv - self._baseline_latency_cv_threshold)
            / self._baseline_latency_cv_threshold
        ) * 100

        if not stable:
            self._logger.debug(
                f"System is not stable. Latency average is {round(latency_ave_pct,4)}% of threshold and latency cv is {round(latency_cv_pct,2)}% of threshold."
            )
        return stable

    def get_current_latency_stats(
        self, time_window: Optional[int] = None
    ) -> SessionStats:
        """Obtains current latency statistics over sliding window from the adapter."""
        if isinstance(self._adapter, Adapter):
            # Get the baseline latency statistics.
            return self._adapter.get_latency_stats(time_window=time_window)
        else:
            if not self._adapter:
                msg = f"Adapter has not be initialized in {self.__class__.__name__}."
                self._logger.exception(msg=msg)
                raise RuntimeError(msg)
            else:
                msg = f"Expected Adapter, got {type(self._adapter).__name__}"
                self._logger.exception(msg)
                raise TypeError(msg)

    def set_baseline_latency_stats(self) -> None:
        """Obtains baseline latency statistics from the adapter."""
        if isinstance(self._adapter, Adapter):
            # Get the baseline latency statistics.
            self._baseline_latency_stats = self._adapter.get_latency_stats()
        else:
            if not self._adapter:
                msg = f"Adapter has not be initialized in {self.__class__.__name__}."
                self._logger.exception(msg=msg)
                raise RuntimeError(msg)
            else:
                msg = f"Expected Adapter, got {type(self._adapter).__name__}"
                self._logger.exception(msg)
                raise TypeError(msg)

        self._logger.debug(f"\nBaseline Latency\n{self._baseline_latency_stats}")

    def _in_stabilization_period(self) -> bool:
        if (
            self._step_clock.is_active()
            and self._step_clock.has_elapsed(self._config.step_duration)
            or not self._step_clock.is_active()
        ):
            if self._stabilization_period:
                self._logger.info(
                    f"{self.__class__.__name__} exiting stabilization period."
                )
            self._stabilization_period = False
        else:
            if not self._stabilization_period:
                self._logger.info(
                    f"{self.__class__.__name__} entering stabilization period."
                )
            self._stabilization_period = True
        return self._stabilization_period


# ------------------------------------------------------------------------------------------------ #
#                              ADAPTER RATE EXPLORE STAGE                                          #
# ------------------------------------------------------------------------------------------------ #
class AdapterRateExploreStage(AdapterExploreExploitStage):
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

        # Placeholder for the next stage, set later.
        self._next_stage: Optional[AdapterConcurrencyExploreStage] = None

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

    def adapt(self) -> None:
        super().adapt()

    def begin_stage(self) -> None:
        super().begin_stage()

    def initialize_session_control(self) -> None:
        super().initialize_session_control()
        self._rate = SessionControlValue(
            initial_value=float(self._config.rate.base),
            min_value=float(self._config.rate.min),
            max_value=float(self._config.rate.max),
            additive_factor=float(self._config.step_increase),
            multiplicative_factor=float(self._config.step_decrease),
            temperature=float(self._config.temperature),
        )

    def begin_session(self) -> None:
        super().begin_session()

    def execute_session(self) -> SessionControl:
        """
        Adjusts the session control values based on session history and transitions to the next stage if appropriate.

        This method adds noise to the rate, creates a session control object, and sets it to the adapter.
        It also checks if the stage should transition to the next one.

        Args:
            history (SessionHistory): Historical data of the session used for validation and adaptation.
        """

        # Determine whether to adapt or stabilize based on the step clock.
        if self._in_stabilization_period():
            self._stabilize()

        else:
            self._adapt()

        # Update the adapter with the current session control data.
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
            self.next_stage, AdapterConcurrencyExploreStage
        ):
            self._adapter.transition(self.next_stage)

    def _adapt(self) -> None:
        """Conduct adaptation by adjusting the rate based on system stability."""
        if self.system_stable():
            # If the system is stable, increase the rate.
            self._rate.increase_value()
        else:
            # If the system is unstable, decrease the rate.
            self._rate.decrease_value()
        # Enter stabilization period
        self._step_clock.start()
        self._stabilization_period = True

        self._logger.debug(f"\n\n{self.__class__.__name__} in a stabilization period.")

    def _stabilize(self) -> None:
        """Apply noise to the rate during the stabilization period."""

        self._rate.add_noise()

    def _validate_next_stage(self) -> None:
        """
        Validates that the next stage is correctly initialized and of the expected type.

        Raises:
            RuntimeError: If the next stage is not initialized.
            TypeError: If the next stage is not of type AdapterRateExploreStage.

        """
        if self.next_stage is None:
            msg = f"Next stage is not initialized in {self.__class__.__name__}."
            self._logger.exception(msg)
            raise RuntimeError(msg)

        if not isinstance(self.next_stage, AdapterConcurrencyExploreStage):
            msg = f"Expected AdapterConcurrencyExploreStage, got {type(self.next_stage).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)


# ------------------------------------------------------------------------------------------------ #
#                              ADAPTER CONCURRENCY EXPLORE STAGE                                   #
# ------------------------------------------------------------------------------------------------ #
class AdapterConcurrencyExploreStage(AdapterExploreExploitStage):
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

        # Placeholder for the next stage, set later.
        self._next_stage: Optional[AdapterExploitStage] = None

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

    def adapt(self) -> None:
        super().adapt()

    def begin_stage(self) -> None:
        super().begin_stage()

    def initialize_session_control(self) -> None:
        super().initialize_session_control()
        self._concurrency = SessionControlValue(
            initial_value=float(self._config.concurrency.base),
            min_value=float(self._config.concurrency.min),
            max_value=float(self._config.concurrency.max),
            additive_factor=float(self._config.step_increase),
            multiplicative_factor=float(self._config.step_decrease),
        )
        # Overriding default rate with that from the prior stage.
        if isinstance(self._adapter, Adapter):
            self._rate = SessionControlValue(
                initial_value=float(self._adapter.session_control.rate),
                min_value=float(self._config.rate.min),
                max_value=float(self._config.rate.max),
                temperature=float(self._config.temperature),
            )

    def begin_session(self) -> None:
        super().begin_session()

    def execute_session(self) -> SessionControl:
        """
        Adjusts the session control values based on session history and transitions to the next stage if appropriate.

        This method adds noise to the rate, creates a session control object, and sets it to the adapter.
        It also checks if the stage should transition to the next one.

        Args:
            history (SessionHistory): Historical data of the session used for validation and adaptation.
        """

        # Determine whether to adapt or stabilize based on the step clock.
        if self._in_stabilization_period():
            self._stabilize()

        else:
            self._adapt()

        # Update the adapter with the current session control data.
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
            self.next_stage, AdapterExploitStage
        ):
            self._adapter.transition(self.next_stage)

    def _adapt(self) -> None:
        """Conduct adaptation by adjusting the rate based on system stability."""
        if self.system_stable():
            # If the system is stable, increase the rate.
            self._concurrency.increase_value()
        else:
            # If the system is unstable, decrease the rate.
            self._concurrency.decrease_value()
        self._step_clock.start()
        self._stabilization_period = True

        self._logger.debug(f"\n\n{self.__class__.__name__} in a stabilization period.")

    def _stabilize(self) -> None:
        """Apply noise to the rate during the stabilization period."""
        self._rate.add_noise()

    def _validate_next_stage(self) -> None:
        """
        Validates that the next stage is correctly initialized and of the expected type.

        Raises:
            RuntimeError: If the next stage is not initialized.
            TypeError: If the next stage is not of type AdapterExploitStage.

        """
        if self.next_stage is None:
            msg = f"Next stage is not initialized in {self.__class__.__name__}."
            self._logger.exception(msg)
            raise RuntimeError(msg)

        if not isinstance(self.next_stage, AdapterExploitStage):
            msg = f"Expected AdapterExploitStage, got {type(self.adapter).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)


# ------------------------------------------------------------------------------------------------ #
#                                ADAPTER EXPLOIT STAGE                                             #
# ------------------------------------------------------------------------------------------------ #
class AdapterExploitStage(AdapterExploreExploitStage):
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

        # Placeholder for the next stage, set later.
        self._next_stage: Optional[AdapterBaselineStage] = None

        self._duration: float = float(self._config.duration)

    @property
    def next_stage(self) -> Optional[AdapterBaselineStage]:
        """
        Gets the next stage of the adapter.

        Returns:
            Optional[AdapterBaselineStage]: The next stage to transition to, or None if not set.
        """
        return self._next_stage

    @next_stage.setter
    def next_stage(self, next_stage: AdapterBaselineStage) -> None:
        """
        Sets the next stage of the adapter.

        Args:
            next_stage (AdapterBaselineStage): The stage to transition to after the baseline stage.
        """
        self._next_stage = next_stage

    def begin_stage(self) -> None:
        super().begin_stage()

    def initialize_session_control(self) -> None:
        super().initialize_session_control()

        # Overriding default rate and concurrency with that from the prior stage.
        if isinstance(self._adapter, Adapter):
            self._concurrency = SessionControlValue(
                initial_value=float(self._adapter.session_control.concurrency),
                min_value=float(self._config.concurrency.min),
                max_value=float(self._config.concurrency.max),
            )
            self._rate = SessionControlValue(
                initial_value=float(self._adapter.session_control.concurrency),
                min_value=float(self._config.rate.min),
                max_value=float(self._config.rate.max),
            )

    def begin_session(self) -> None:
        super().begin_session()

    def execute_session(self) -> SessionControl:
        """
        Adjusts the session control values based on session history and transitions to the next stage if appropriate.

        This method adds noise to the rate, creates a session control object, and sets it to the adapter.
        It also checks if the stage should transition to the next one.

        Args:
            history (SessionHistory): Historical data of the session used for validation and adaptation.
        """

        # Get current statistics
        current_latency_stats = self.get_current_latency_stats(
            time_window=self._config.window_size
        )

        # Compute Latency and CV Ratio
        if isinstance(self._baseline_latency_stats, SessionStats):
            latency_ratio = (
                current_latency_stats.average / self._baseline_latency_stats.average
            )
            cv_ratio = current_latency_stats.cv / self._baseline_latency_stats.cv
        # Compute new request rate
        self._rate.value = (
            self._rate.value
            * (1 - self._config.k * (latency_ratio - 1))
            * (1 - self._config.m * (cv_ratio - 1))
        )
        # Update the adapter with the current session control data.
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
            self.next_stage, AdapterBaselineStage
        ):
            self._adapter.transition(self.next_stage)

    def _validate_next_stage(self) -> None:
        """
        Validates that the next stage is correctly initialized and of the expected type.

        Raises:
            RuntimeError: If the next stage is not initialized.
            TypeError: If the next stage is not of type AdapterBaselineStage.

        """
        if self.next_stage is None:
            msg = f"Next stage is not initialized in {self.__class__.__name__}."
            self._logger.exception(msg)
            raise RuntimeError(msg)

        if not isinstance(self.next_stage, AdapterBaselineStage):
            msg = f"Expected AdapterBaselineStage, got {type(self.adapter).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)
