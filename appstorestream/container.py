#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/container.py                                                        #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 04:17:11 am                                                 #
# Modified   : Friday August 16th 2024 10:21:59 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Framework Dependency Container"""
import logging
import logging.config  # pragma: no cover

from dependency_injector import containers, providers

from appstorestream.domain.base.state import CircuitBreaker
from appstorestream.infra.base.config import Config
from appstorestream.infra.database.mysql import MySQLDatabase
from appstorestream.infra.metrics.session import Metrics
from appstorestream.infra.repo.appdata import AppDataRepo
from appstorestream.infra.repo.job import JobRepo
from appstorestream.infra.repo.project import ProjectRepo
from appstorestream.infra.repo.review import ReviewRepo
from appstorestream.infra.repo.uow import UoW
from appstorestream.infra.web.asession import ASessionAppData, ASessionReview
from appstorestream.infra.web.throttle import AThrottle, AThrottleHistory


# ------------------------------------------------------------------------------------------------ #
#                                        LOGGING                                                   #
# ------------------------------------------------------------------------------------------------ #
class LoggingContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    logging = providers.Resource(
        logging.config.dictConfig,
        config=config.logging,
    )


# ------------------------------------------------------------------------------------------------ #
#                                      PERSISTENCE                                                 #
# ------------------------------------------------------------------------------------------------ #
class PersistenceContainer(containers.DeclarativeContainer):

    database = providers.Singleton(MySQLDatabase)

    appdata_repo = providers.Singleton(AppDataRepo, database=database)

    review_repo = providers.Singleton(ReviewRepo, database=database)

    job_repo = providers.Singleton(JobRepo, database=database)

    project_repo = providers.Singleton(ProjectRepo, database=database)

    uow = providers.Singleton(
        UoW,
        database=database,
        appdata_repo=appdata_repo,
        review_repo=review_repo,
        job_repo=job_repo,
        project_repo=project_repo,
    )


# ------------------------------------------------------------------------------------------------ #
#                                         STATE                                                    #
# ------------------------------------------------------------------------------------------------ #
class StateContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    circuit_breaker = providers.Singleton(
        CircuitBreaker,
        closed_window_size=config.circuit_breaker.closed_window_size,
        closed_burnin_period=config.circuit_breaker.closed_burnin_period,
        closed_failure_rate_threshold=config.circuit_breaker.closed_failure_rate_threshold,
        half_open_window_size=config.circuit_breaker.half_open_window_size,
        half_open_failure_rate_threshold=config.circuit_breaker.half_open_failure_rate_threshold,
        half_open_delay=config.circuit_breaker.half_open_delay,
        short_circuit_errors_window_size=config.circuit_breaker.short_circuit_errors_window_size,
        short_circuit_errors_failure_rate_threshold=config.circuit_breaker.short_circuit_errors_failure_rate_threshold,
        short_circuit_404s_window_size=config.circuit_breaker.short_circuit_404s_window_size,
        short_circuit_404s_failure_rate_threshold=config.circuit_breaker.short_circuit_404s_failure_rate_threshold,
        open_cooldown_period=config.circuit_breaker.open_cooldown_period,
    )


# ------------------------------------------------------------------------------------------------ #
#                                    WEB CONTAINER                                                 #
# ------------------------------------------------------------------------------------------------ #
class WebContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    metrics = providers.Singleton(Metrics, port=config.monitor.prometheus_client_port)

    athrottle = providers.Singleton(
        AThrottle,
        athrottle_history=AThrottleHistory(),
        burnin_length=config.athrottle.burnin_length,
        explore_length=config.athrottle.explore_length,
        exploit_length=config.athrottle.exploit_length,
        current_stage=0,
        concurrency=config.athrottle.concurrency,
        rate=config.athrottle.rate,
        temperature=config.athrottle.temperature,
        exploration_heatup_step_size=config.athrottle.exploration_heatup_step_size,
        exploration_cooldown_step_size=config.athrottle.exploration_cooldown_step_size,
        threshold=config.athrottle.threshold,
        k=config.athrottle.k,
        min_rate=config.athrottle.min_rate,
        max_rate=config.athrottle.max_rate,
    )

    asession_appdata = providers.Singleton(
        ASessionAppData,
        throttle=athrottle,
        max_concurrency=config.asession.max_concurrency,
        retries=config.asession.retries,
        timeout=config.asession.timeout,
        metrics=metrics,
    )

    asession_review = providers.Singleton(
        ASessionReview,
        throttle=athrottle,
        max_concurrency=config.asession.max_concurrency,
        retries=config.asession.retries,
        timeout=config.asession.timeout,
        metrics=metrics,
    )


# ------------------------------------------------------------------------------------------------ #
#                                       FRAMEWORK                                                  #
# ------------------------------------------------------------------------------------------------ #
class AppStoreStreamContainer(containers.DeclarativeContainer):

    config_filepath = Config().filepath

    config = providers.Configuration(yaml_files=[config_filepath])

    logs = providers.Container(LoggingContainer, config=config)

    data = providers.Container(PersistenceContainer)

    state = providers.Container(StateContainer, config=config)

    web = providers.Container(WebContainer, config=config)
