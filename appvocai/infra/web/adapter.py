#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/infra/web/adapter.py                                                      #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 04:44:47 am                                                   #
# Modified   : Tuesday August 27th 2024 06:26:13 pm                                                #
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

from appvocai.core.data import NestedNamespace
from appvocai.infra.web.profile import (
    SessionControl,
    SessionHistory,
    SessionStats,
    StatisticalSnapshot,
)


# ------------------------------------------------------------------------------------------------ #
#                                        CLOCK                                                     #
# ------------------------------------------------------------------------------------------------ #
class Clock:
    """A simple clock utility to track elapsed time.

    This class provides methods to start, reset, and measure elapsed time,
    useful for timing operations or managing delays in asynchronous processes.
    """

    def __init__(self) -> None:
        """Initializes the Clock instance.

        The clock starts in a reset state with `_start_time` set to 0.0.
        """
        self._start_time: Optional[float] = 0.0

    def start(self) -> None:
        """Starts or restarts the clock.

        Sets `_start_time` to the current time. This method can be called multiple
        times to restart the clock.
        """
        self._start_time = time.time()

    def reset(self) -> None:
        """Resets the clock to zero.

        Sets `_start_time` to 0.0, effectively stopping the clock.
        """
        self._start_time = 0.0

    def elapsed(self) -> float:
        """Returns the time elapsed since the clock was started.

        Raises:
            RuntimeError: If the clock has not been started.

        Returns:
            float: The time elapsed in seconds since the clock was started.
        """
        if self._start_time is None:
            raise RuntimeError("Clock has not been started.")
        return time.time() - self._start_time

    def has_elapsed(self, response_time: float) -> bool:
        """Checks if a given response_time has elapsed.

        Args:
            response_time (float): The response_time to check against, in seconds.

        Returns:
            bool: True if the specified response_time has elapsed since the clock was started,
            False otherwise.
        """
        return self.elapsed() >= response_time

    def is_active(self) -> bool:
        """Checks if the clock is active.

        The clock is considered active if it has been started and not reset.

        Returns:
            bool: True if the clock is active, False otherwise.
        """
        return self._start_time != 0.0


# ------------------------------------------------------------------------------------------------ #
#                                ADAPTER VALUE MIXIN                                               #
# ------------------------------------------------------------------------------------------------ #
class SessionControlValue:
    """Manages adaptive control values like request rate and concurrency.

    This class provides methods to adjust a control value, such as request
    rate or concurrency, within specified minimum and maximum bounds.
    The value can be increased additively or decreased multiplicatively,
    with optional noise for stochastic behavior.

    Attributes:
        _initial_value (float): The initial value of the control parameter.
        _value (float): The current value of the control parameter.
        _min_value (float): The minimum allowed value for the control parameter.
        _max_value (float): The maximum allowed value for the control parameter.
        _additive_factor (float): The amount added to the value during increase operations.
        _multiplicative_factor (float): The factor by which the value is multiplied during decrease operations.
        _temperature (float): The standard deviation of the noise added to the value.
    """

    def __init__(
        self,
        initial_value: float = 50.0,
        min_value: float = 50.0,
        max_value: float = 500.0,
        additive_factor: float = 0.9,
        multiplicative_factor: float = 1.0,
        temperature: float = 0.0,
    ) -> None:
        """Initializes the SessionControlValue with constraints and adjustment factors.

        Args:
            initial_value (float): The starting value of the control parameter. Defaults to 50.0.
            min_value (float): The minimum allowable value. Defaults to 50.0.
            max_value (float): The maximum allowable value. Defaults to 500.0.
            additive_factor (float): The amount to add during increase operations. Defaults to 0.9.
            multiplicative_factor (float): The factor to multiply during decrease operations. Defaults to 1.0.
            temperature (float, optional): The standard deviation of the noise to add to the value. Defaults to 0.0.
        """
        self._initial_value = initial_value
        self._value = initial_value
        self._min_value = min_value
        self._max_value = max_value
        self._additive_factor = additive_factor
        self._multiplicative_factor = multiplicative_factor
        self._temperature = temperature

    @property
    def value(self) -> float:
        """Gets the current control value.

        Returns:
            float: The current control value.
        """
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        """Sets the control value.

        Args:
            value (float): The new value for the control parameter.
        """
        self._value = value

    def increase_value(self, noise: bool = True) -> None:
        """Increases the control value additively, respecting constraints.

        The value is increased by the additive factor. If noise is enabled,
        a normally distributed random value is added. The result is clamped
        to the maximum value.

        Args:
            noise (bool): Whether to add noise to the increase. Defaults to True.
        """
        new_value = self._value + self._additive_factor
        if noise:
            new_value += np.random.normal(loc=0, scale=self._temperature)
        self._value = min(new_value, self._max_value)

    def decrease_value(self, noise: bool = True) -> None:
        """Decreases the control value multiplicatively, respecting constraints.

        The value is multiplied by the multiplicative factor. If noise is enabled,
        a normally distributed random value is added. The result is clamped
        to the minimum value.

        Args:
            noise (bool): Whether to add noise to the decrease. Defaults to True.
        """
        new_value = self._value * self._multiplicative_factor
        if noise:
            new_value += np.random.normal(loc=0, scale=self._temperature)
        self._value = max(new_value, self._min_value)

    def reset_value(self) -> None:
        """Resets the control value to its initial value.

        This method restores the control value to its initial value as
        defined during initialization.
        """
        self._value = self._initial_value

    def add_noise(self) -> None:
        """Adds noise to the current control value.

        A normally distributed random value, based on the temperature
        (standard deviation), is added to the current value. The result
        is clamped to remain within the minimum and maximum bounds.
        """
        noise = np.random.normal(loc=0, scale=self._temperature)
        self._value += noise
        # Ensure value stays within min/max bounds
        self._value = min(max(self._value, self._min_value), self._max_value)


# ------------------------------------------------------------------------------------------------ #
#                                        ADAPTER                                                   #
# ------------------------------------------------------------------------------------------------ #
class Adapter:
    """Manages the adaptive behavior for session control using the State Design Pattern.

    The `Adapter` class acts as the context in the State Design Pattern, managing
    the current stage of the session control process. It provides methods to transition
    between stages, adapt control values based on session history, and retrieve
    statistical data.

    Attributes:
        _session_history (SessionHistory): Tracks the history of session metrics.
        _session_control (SessionControl): Manages the control values for the session, such as rate and concurrency.
        _logger (logging.Logger): Logger instance for the adapter.
        _stage (AdapterStage): The current stage in the adaptive process.
    """

    def __init__(self, initial_stage: AdapterBaselineStage) -> None:
        """Initializes the Adapter with a starting stage.

        Args:
            initial_stage (AdapterBaselineStage): The initial stage to start the adaptation process.
        """
        self._session_history: SessionHistory = SessionHistory()
        self._session_control: SessionControl = SessionControl()
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.transition_to_stage(stage=initial_stage)

    @property
    def session_control(self) -> SessionControl:
        """Gets the current session control.

        Returns:
            SessionControl: The current session control object managing adaptive values.
        """
        return self._session_control

    @session_control.setter
    def session_control(self, session_control: SessionControl) -> None:
        """Sets the session control, ensuring it's a valid `SessionControl` object.

        Args:
            session_control (SessionControl): The new session control object.

        Raises:
            TypeError: If the provided `session_control` is not a valid `SessionControl` object.
        """
        if not isinstance(session_control, SessionControl):
            msg = "Type Error: session_control is not a valid SessionControl object."
            self._logger.exception(msg)
            raise TypeError(msg)
        self._session_control = session_control

    @property
    def stage(self) -> AdapterStage:
        """Gets the current stage in the adaptation process.

        Returns:
            AdapterStage: The current stage object.
        """
        return self._stage

    @stage.setter
    def stage(self, stage: AdapterStage) -> None:
        """Sets the current stage, ensuring it's a valid `AdapterStage` object.

        Args:
            stage (AdapterStage): The new stage object.

        Raises:
            TypeError: If the provided `stage` is not a valid `AdapterStage` object.
        """
        if not isinstance(stage, AdapterStage):
            msg = "Type Error: stage is not a valid AdapterStage object."
            self._logger.exception(msg)
            raise TypeError(msg)
        self._stage = stage

    def adapt_requests(self, history: SessionHistory) -> None:
        """Adapts the control values based on the session history.

        This method sets the session history and delegates the adaptation logic to the current stage.

        Args:
            history (SessionHistory): The session history containing metrics for adaptation.
        """
        self._session_history = history
        self._stage.adapt_requests()

    def transition_to_stage(self, stage: AdapterStage) -> None:
        """Transitions to a new stage in the adaptive process.

        This method logs the transition and updates the current stage.

        Args:
            stage (AdapterStage): The new stage to transition to.
        """
        self._logger.info(
            f"{self.__class__.__name__} transitioning to {stage.__class__.__name__}"
        )
        self._stage = stage
        self._stage.adapter = self

    def get_latency_stats(self, time_window: Optional[int] = None) -> SessionStats:
        """Retrieves latency statistics over a given time window.

        Args:
            time_window (Optional[int]): The time window in seconds for which to compute latency stats. If None, computes for the entire session.

        Returns:
            SessionStats: The computed latency statistics.
        """
        return self._session_history.get_latency_stats(time_window=time_window)

    def get_snapshot(self, time_window: Optional[int] = None) -> StatisticalSnapshot:
        """Retrieves a statistical snapshot of session metrics over a given time window.

        Args:
            time_window (Optional[int]): The time window in seconds for which to take the snapshot. If None, computes for the entire session.

        Returns:
            StatisticalSnapshot: The snapshot of the session's statistical data.
        """
        return self._session_history.get_snapshot(time_window=time_window)


# ------------------------------------------------------------------------------------------------ #
#                                     ADAPTER STAGE                                                #
# ------------------------------------------------------------------------------------------------ #
class AdapterStage(ABC):
    """Abstract base class for Adapter stages.

    This class defines the interface and common properties for different stages
    of an adapter. Each stage is responsible for handling rate and concurrency
    adjustments, transitioning to the next stage, and validating the adapter and
    history objects.

    Args:
        config (ConfigurationOption): Configuration parameters for the stage.

    Attributes:
        _config (NestedNamespace): A nested namespace object containing the configuration parameters.
        _adapter (Optional[Adapter]): The current adapter associated with the stage, initially None.
        _stage_clock (Clock): A clock object used to track the response_time of the stage.
        _rate (SessionControlValue): The current rate control value.
        _concurrency (SessionControlValue): The current concurrency control value.
        _logger (logging.Logger): Logger instance for the class.
    """

    def __init__(self, config: ConfigurationOption) -> None:
        """Initializes the AdapterStage with the given configuration.

        Args:
            config (ConfigurationOption): The configuration parameters for the stage.
        """
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
        """Returns the next stage in the sequence.

        Returns:
            Optional[AdapterStage]: The next stage in the sequence, or None if there is no next stage.
        """
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

    def adapt_requests(self) -> None:
        """Executes the adapter methods for the current stage.

        This method orchestrates the flow of the session by beginning the stage,
        executing the core logic, and ending the session with any necessary transitions.
        """
        self.begin_session()
        session_control = self.execute_session()
        self.end_session(session_control=session_control)

    def begin_stage(self) -> None:
        """Starts the stage clock and initializes session control.

        This method is called at the beginning of the stage to prepare the environment
        for the session.
        """
        self._stage_clock.start()
        self.initialize_session_control()

    def initialize_session_control(self) -> None:
        """Method for subclasses to override the default session control.

        Subclasses can implement this method if they need to provide specific
        initialization logic for session control.
        """
        pass

    def begin_session(self) -> None:
        """Performs stage startup processes.

        This method validates the adapter and the next stage, and starts the stage clock
        if it is not already active.
        """
        self._validate_adapter()
        self._validate_next_stage()
        if not self._stage_clock.is_active():
            self.begin_stage()

    @abstractmethod
    def execute_session(self) -> SessionControl:
        """Performs the core logic of the stage.

        This method must be implemented by subclasses to define the main behavior of the stage.

        Returns:
            SessionControl: The session control object containing the updated rate and concurrency.
        """
        pass

    def end_session(self, session_control: SessionControl) -> None:
        """Finalizes the session and checks for stage transitions.

        This method updates the adapter with the current session control values and determines
        if the stage response_time has elapsed, triggering a transition if necessary.

        Args:
            session_control (SessionControl): The session control object containing the updated rate and concurrency.
        """
        if isinstance(self._adapter, Adapter):
            self._adapter.session_control = session_control

        if self._stage_clock.has_elapsed(
            response_time=float(self._config.response_time)
        ):
            self.end_stage()

    def end_stage(self) -> None:
        """Finalizes the stage and triggers the transition to the next stage.

        This method resets the stage clock and calls the transition method to move to the next stage.
        """
        self._stage_clock.reset()
        self.transition_to_stage()

    @abstractmethod
    def transition_to_stage(self) -> None:
        """Performs transition to the next stage if complete.

        This method must be implemented by subclasses to define the logic for transitioning
        to the next stage in the sequence.
        """
        pass

    @abstractmethod
    def _validate_next_stage(self) -> None:
        """Validates the next stage object.

        This method must be implemented by subclasses to ensure that the next stage is correctly
        configured before transitioning.

        Raises:
            TypeError: If the next stage is not of the expected type.
        """
        pass

    def _validate_adapter(self) -> None:
        """Validates the adapter object.

        This method checks that the adapter is correctly initialized and of the expected type.

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
        _response_time (float): Duration of the baseline stage.
        _next_stage (Optional[AdapterRateExploreStage]): The next stage to transition to.
    """

    def __init__(self, config: ConfigurationOption) -> None:
        """
        Initializes the AdapterBaselineStage with the provided configuration.

        Args:
            config (ConfigurationOption): Configuration dictionary containing
                rate, min_rate, max_rate, temperature, concurrency, and response_time settings.

        Initializes:
            _rate (SessionControlValue): Session control object for rate with noise adjustment.
            _concurrency (float): Concurrency value during this stage.
            _response_time (float): Duration of the baseline stage.
            _next_stage (Optional[AdapterRateExploreStage]): The next stage, initially set to None.
        """
        super().__init__(config=config)

        self._response_time: float = float(self._config.response_time)
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
        """
        Starts the stage by initializing the stage clock and session control.
        """
        super().begin_stage()

    def initialize_session_control(self) -> None:
        """
        Initializes the session control values for the baseline stage.
        """
        super().initialize_session_control()

    def begin_session(self) -> None:
        """
        Prepares the session by validating the adapter and starting the session.
        """
        super().begin_session()

    def execute_session(self) -> SessionControl:
        """
        Adjusts the session control values based on the current configuration.

        This method adds noise to the rate, creates a session control object,
        and prepares the adapter for the next stage transition.

        Returns:
            SessionControl: The session control object containing the updated rate and concurrency.
        """
        self._rate.add_noise()
        # Create a session control object for the adapter
        return SessionControl(
            rate=self._rate.value, concurrency=self._concurrency.value
        )

    def end_session(self, session_control: SessionControl) -> None:
        """
        Finalizes the session and checks for stage transition.

        This method determines if the current stage should end and if so,
        triggers the transition to the next stage.

        Args:
            session_control (SessionControl): The session control object containing the updated rate and concurrency.
        """
        super().end_session(session_control=session_control)

    def end_stage(self) -> None:
        """
        Finalizes the baseline stage and prepares for the transition to the next stage.
        """
        super().end_stage()

    def transition_to_stage(self) -> None:
        """
        Transitions to the next stage if the current stage has ended.

        If the baseline stage is complete and the next stage is properly set,
        this method will trigger the adapter to transition to the next stage.
        """
        if isinstance(self._adapter, Adapter) and isinstance(
            self.next_stage, AdapterRateExploreStage
        ):
            self._adapter.transition_to_stage(self.next_stage)

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
class AdapterExploreExploitStage(AdapterStage, ABC):
    """Abstract base class for stages that explore values of rate and concurrency."""

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

    @abstractmethod
    def execute_session(self) -> SessionControl:
        """This method must be implemented by subclasses to execute the session logic."""
        pass

    def adapt_requests(self) -> None:
        """Optional override for subclasses to adapt requests during the session."""
        super().adapt_requests()

    def begin_stage(self) -> None:
        """Optional override for subclasses to initialize the stage."""
        super().begin_stage()
        self.set_baseline_latency_stats()

    def initialize_session_control(self) -> None:
        """Optional override for subclasses to set up session control parameters."""
        super().initialize_session_control()

    def begin_session(self) -> None:
        """Optional override for subclasses to perform actions at the start of a session."""
        super().begin_session()

    def end_session(self, session_control: SessionControl) -> None:
        """Optional override for subclasses to perform actions at the end of a session."""
        super().end_session(session_control=session_control)

    def end_stage(self) -> None:
        """Optional override for subclasses to clean up or finalize the stage."""
        super().end_stage()

    def system_stable(self) -> bool:
        """Evaluates system stability based on latency statistics."""
        current_latency_stats = self.get_current_latency_stats()

        self._set_latency_thresholds()

        stable = self._is_latency_within_threshold(current_latency_stats)

        if not stable:
            self._log_unstable_system(current_latency_stats)
        return stable

    def get_current_latency_stats(
        self, time_window: Optional[int] = None
    ) -> SessionStats:
        """Obtains current latency statistics over a sliding window from the adapter."""
        if isinstance(self._adapter, Adapter):
            return self._adapter.get_latency_stats(time_window=time_window)
        else:
            if not self._adapter:
                msg = f"Adapter has not been initialized in {self.__class__.__name__}."
                self._logger.exception(msg=msg)
                raise RuntimeError(msg)
            else:
                msg = f"Expected Adapter, got {type(self._adapter).__name__}"
                self._logger.exception(msg)
                raise TypeError(msg)

    def set_baseline_latency_stats(self) -> None:
        """Obtains baseline latency statistics from the adapter."""
        if isinstance(self._adapter, Adapter):
            self._baseline_latency_stats = self._adapter.get_latency_stats(
                time_window=self._config.window_size
            )
        else:
            if not self._adapter:
                msg = f"Adapter has not been initialized in {self.__class__.__name__}."
                self._logger.exception(msg=msg)
                raise RuntimeError(msg)
            else:
                msg = f"Expected Adapter, got {type(self._adapter).__name__}"
                self._logger.exception(msg)
                raise TypeError(msg)

        self._logger.debug(f"\nBaseline Latency\n{self._baseline_latency_stats}")

    def _set_latency_thresholds(self) -> None:
        self._baseline_latency_ave_threshold = (
            self._baseline_latency_stats.average * self._config.threshold
        )
        self._baseline_latency_cv_threshold = (
            self._baseline_latency_stats.cv * self._config.threshold
        )

    def _is_latency_within_threshold(self, stats: SessionStats) -> bool:
        return (
            stats.average <= self._baseline_latency_ave_threshold
            and stats.cv <= self._baseline_latency_cv_threshold
        )

    def _log_unstable_system(self, stats: SessionStats) -> None:
        latency_ave_pct = (
            (stats.average - self._baseline_latency_ave_threshold)
            / self._baseline_latency_ave_threshold
        ) * 100
        latency_cv_pct = (
            (stats.cv - self._baseline_latency_cv_threshold)
            / self._baseline_latency_cv_threshold
        ) * 100

        self._logger.debug(
            f"System is not stable. Latency average is {round(latency_ave_pct, 4)}% of threshold and latency cv is {round(latency_cv_pct, 2)}% of threshold."
        )

    def _in_stabilization_period(self) -> bool:
        if self._should_exit_stabilization():
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

    def _should_exit_stabilization(self) -> bool:
        return (
            self._step_clock.is_active()
            and self._step_clock.has_elapsed(self._config.step_response_time)
            or not self._step_clock.is_active()
        )


# ------------------------------------------------------------------------------------------------ #
#                              ADAPTER RATE EXPLORE STAGE                                          #
# ------------------------------------------------------------------------------------------------ #
class AdapterRateExploreStage(AdapterExploreExploitStage):
    """
    Represents the exploration stage of an adapter for rate control in a session.

    This stage manages the adaptation of the session rate based on system stability
    and historical session data. It allows for the adjustment of rates while ensuring
    proper transitions to the next stage.

    Attributes:
        _next_stage (Optional[AdapterConcurrencyExploreStage]): The next stage to transition to,
            initially set to None.
    """

    def __init__(self, config: ConfigurationOption) -> None:
        """
        Initializes the AdapterRateExploreStage with the provided configuration.

        Args:
            config (ConfigurationOption): Configuration dictionary containing rate,
                min_rate, max_rate, temperature, concurrency, and response_time settings.

        Initializes:
            _rate (SessionControlValue): Session control object for rate with noise adjustment.
            _concurrency (float): Concurrency value during this stage.
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
            next_stage (AdapterConcurrencyExploreStage): The stage to transition to after
                the exploration stage.
        """
        self._next_stage = next_stage

    def adapt_requests(self) -> None:
        """
        Adjusts the request parameters based on the current adaptation logic.

        This method is called to potentially modify request parameters for the ongoing session.
        """
        super().adapt_requests()

    def begin_stage(self) -> None:
        """
        Initializes any necessary components for the start of this stage.

        This method is called at the beginning of the exploration stage to prepare the adapter
        for execution.
        """
        super().begin_stage()

    def initialize_session_control(self) -> None:
        """
        Initializes the session control values for rate adjustment.

        This method sets up the initial rate control values based on the provided configuration.
        """
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
        """
        Prepares the adapter to begin a new session.

        This method is called to signal the start of a session and any associated preparations.
        """
        super().begin_session()

    def execute_session(self) -> SessionControl:
        """
        Executes the session logic for rate adaptation.

        Adjusts the session control values based on session history and determines if the
        adapter should transition to the next stage.

        Returns:
            SessionControl: An object containing the current rate and concurrency settings.

        Raises:
            RuntimeError: If an error occurs during the session execution.
        """
        if self._in_stabilization_period():
            self._stabilize()
        else:
            self._adapt()

        return SessionControl(
            rate=self._rate.value, concurrency=self._concurrency.value
        )

    def end_session(self, session_control: SessionControl) -> None:
        """
        Determines if the current session should end and prepares for stage transition.

        Args:
            session_control (SessionControl): The session control object to assess completion.

        Returns:
            None
        """
        super().end_session(session_control=session_control)

    def end_stage(self) -> None:
        """
        Cleans up any resources or states related to the end of this stage.

        This method is called at the end of the exploration stage to finalize operations.
        """
        super().end_stage()

    def transition_to_stage(self) -> None:
        """
        Transitions to the next stage if the current stage has ended.

        If the exploration stage is complete and the next stage is properly set,
        this method will trigger the adapter to transition to the next stage.
        """
        if isinstance(self._adapter, Adapter) and isinstance(
            self.next_stage, AdapterConcurrencyExploreStage
        ):
            self._adapter.transition_to_stage(self.next_stage)

    def _adapt(self) -> None:
        """Conducts adaptation by adjusting the rate based on system stability.

        Increases the rate if the system is stable; decreases it if unstable.
        It also starts a stabilization period.

        Returns:
            None
        """
        if self.system_stable():
            self._rate.increase_value()
        else:
            self._rate.decrease_value()

        self._step_clock.start()
        self._stabilization_period = True

        self._logger.debug(f"\n\n{self.__class__.__name__} in a stabilization period.")

    def _stabilize(self) -> None:
        """Applies noise to the rate during the stabilization period.

        This method introduces variability to the rate to allow for exploration of potential values.

        Returns:
            None
        """
        self._rate.add_noise()

    def _validate_next_stage(self) -> None:
        """
        Validates that the next stage is correctly initialized and of the expected type.

        Raises:
            RuntimeError: If the next stage is not initialized.
            TypeError: If the next stage is not of type AdapterConcurrencyExploreStage.
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
    """
    Represents the concurrency exploration stage of an adapter for session control.

    This stage manages the adaptation of concurrency values based on system stability
    and historical session data. It allows for the adjustment of concurrency while ensuring
    proper transitions to the next stage.

    Attributes:
        _next_stage (Optional[AdapterExploitStage]): The next stage to transition to,
            initially set to None.
    """

    def __init__(self, config: ConfigurationOption) -> None:
        """
        Initializes the AdapterConcurrencyExploreStage with the provided configuration.

        Args:
            config (ConfigurationOption): Configuration dictionary containing rate,
                min_rate, max_rate, temperature, concurrency, and response_time settings.

        Initializes:
            _concurrency (SessionControlValue): Session control object for concurrency
                with noise adjustment.
            _response_time (float): Duration of the concurrency exploration stage.
            _next_stage (Optional[AdapterExploitStage]): The next stage, initially set to None.
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
            next_stage (AdapterExploitStage): The stage to transition to after the concurrency
                exploration stage.
        """
        self._next_stage = next_stage

    def adapt_requests(self) -> None:
        """
        Adjusts the requests based on the current adaptation logic.

        This method is called to potentially modify request parameters for the ongoing session.
        """
        super().adapt_requests()

    def begin_stage(self) -> None:
        """
        Initializes any necessary components for the start of this stage.

        This method is called at the beginning of the concurrency exploration stage
        to prepare the adapter for execution.
        """
        super().begin_stage()

    def initialize_session_control(self) -> None:
        """
        Initializes the session control values for concurrency adjustment.

        This method sets up the initial concurrency control values based on the provided configuration
        and overrides the default rate with that from the prior stage.
        """
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
        """
        Prepares the adapter to begin a new session.

        This method is called to signal the start of a session and any associated preparations.
        """
        super().begin_session()

    def execute_session(self) -> SessionControl:
        """
        Executes the session logic for concurrency adaptation.

        This method adjusts the session control values based on session history and determines if the
        adapter should transition to the next stage.

        Returns:
            SessionControl: An object containing the current rate and concurrency settings.
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
        Determines if the current stage should end and prepares for stage transition.

        Checks if the concurrency exploration stage is complete and if so, takes a snapshot
        of the session history and prepares for transition.

        Args:
            session_control (SessionControl): The session control object to assess completion.
        """
        super().end_session(session_control=session_control)

    def end_stage(self) -> None:
        """
        Cleans up any resources or states related to the end of this stage.

        This method is called at the end of the concurrency exploration stage to finalize operations.
        """
        super().end_stage()

    def transition_to_stage(self) -> None:
        """
        Transitions to the next stage if the current stage has ended.

        If the concurrency exploration stage is complete and the next stage is properly set,
        this method will trigger the adapter to transition to the next stage.
        """
        if isinstance(self._adapter, Adapter) and isinstance(
            self.next_stage, AdapterExploitStage
        ):
            self._adapter.transition_to_stage(self.next_stage)

    def _adapt(self) -> None:
        """
        Conducts adaptation by adjusting the concurrency based on system stability.

        Increases the concurrency if the system is stable; decreases it if unstable.
        """
        if self.system_stable():
            # If the system is stable, increase the concurrency.
            self._concurrency.increase_value()
        else:
            # If the system is unstable, decrease the concurrency.
            self._concurrency.decrease_value()

        self._step_clock.start()
        self._stabilization_period = True

        self._logger.debug(f"\n\n{self.__class__.__name__} in a stabilization period.")

    def _stabilize(self) -> None:
        """
        Applies noise to the rate during the stabilization period.

        This method introduces variability to the concurrency to allow for exploration of potential values.
        """
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
            msg = f"Expected AdapterExploitStage, got {type(self.next_stage).__name__}"
            self._logger.exception(msg)
            raise TypeError(msg)


# ------------------------------------------------------------------------------------------------ #
#                                ADAPTER EXPLOIT STAGE                                             #
# ------------------------------------------------------------------------------------------------ #
class AdapterExploitStage(AdapterExploreExploitStage):
    def __init__(self, config: ConfigurationOption) -> None:
        """
        Initializes the AdapterExploitStage with the provided configuration.

        Args:
            config (ConfigurationOption): Configuration dictionary containing settings for
                rate, min_rate, max_rate, temperature, concurrency, and response_time.

        Initializes:
            _rate (SessionControlValue): Session control object for rate with noise adjustment.
            _concurrency (SessionControlValue): Concurrency value during this stage,
                initialized from the previous stage.
            _response_time (float): Duration of the exploit stage, specified in the configuration.
            _next_stage (Optional[AdapterBaselineStage]): The next stage to transition to,
                initially set to None.

        Attributes:
            next_stage (Optional[AdapterBaselineStage]): The next stage to transition to,
                or None if not set.
        """
        super().__init__(config=config)

        # Placeholder for the next stage, set later.
        self._next_stage: Optional[AdapterBaselineStage] = None

        self._response_time: float = float(self._config.response_time)

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
            next_stage (AdapterBaselineStage): The stage to transition to after the exploit stage.
        """
        self._next_stage = next_stage

    def begin_stage(self) -> None:
        """
        Begins the exploit stage, preparing any necessary configurations or state.
        """
        super().begin_stage()

    def initialize_session_control(self) -> None:
        """
        Initializes the session control values for rate and concurrency using the
        configurations and values from the prior stage.
        """
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
        """
        Begins a new session within the exploit stage.
        """
        super().begin_session()

    def execute_session(self) -> SessionControl:
        """
        Adjusts the session control values based on current latency statistics and
        transitions to the next stage if appropriate.

        This method computes the new rate based on latency and coefficient of variation
        ratios compared to baseline statistics.

        Returns:
            SessionControl: The current session control data containing the adjusted rate
            and concurrency values.
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
        Determines if the current session should end and transitions to the next stage.

        This method checks if the exploit stage is complete and prepares for transition
        to the next stage.

        Args:
            session_control (SessionControl): The session control data used to evaluate
            the end of the session.
        """
        super().end_session(session_control=session_control)

    def end_stage(self) -> None:
        """
        Ends the exploit stage, performing any necessary cleanup or finalization.
        """
        super().end_stage()

    def transition_to_stage(self) -> None:
        """
        Transitions to the next stage if the current stage has ended.

        If the exploit stage is complete and the next stage is properly set,
        this method will trigger the adapter to transition to the next stage.
        """
        if isinstance(self._adapter, Adapter) and isinstance(
            self.next_stage, AdapterBaselineStage
        ):
            self._adapter.transition_to_stage(self.next_stage)

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
