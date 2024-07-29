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
# Modified   : Monday July 29th 2024 01:16:29 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Framework Dependency Container"""
import logging
import logging.config  # pragma: no cover

from dependency_injector import containers, providers

from appstorestream.application.base.job import JobConfig
from appstorestream.application.base.state import CircuitBreaker
from appstorestream.infra.database.mysql import MySQLDatabase
from appstorestream.infra.repo.appdata import AppDataRepo
from appstorestream.infra.repo.job import JobRepo
from appstorestream.infra.repo.project import ProjectRepo
from appstorestream.infra.repo.review import ReviewRepo
from appstorestream.infra.repo.uow import UoW
from appstorestream.infra.web.asession import ASessionAppData, ASessionReview
from appstorestream.infra.web.throttle import AThrottle


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

    project_repo = providers.Singleton(ProjectRepo)

    uow = providers.Singleton(UoW,
                              database=database,
                              appdata_repo=appdata_repo,
                              review_repo=review_repo,
                              job_repo=job_repo,
                              project_repo=project_repo)


# ------------------------------------------------------------------------------------------------ #
#                                          JOB                                                     #
# ------------------------------------------------------------------------------------------------ #
class JobContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    job_config = providers.Singleton(JobConfig, **config.job)

# ------------------------------------------------------------------------------------------------ #
#                                         STATE                                                    #
# ------------------------------------------------------------------------------------------------ #
class StateContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    circuit_breaker = providers.Singleton(CircuitBreaker,
                            closed_window_size = config.circuit_breaker.closed.window_size,
                            closed_burnin_period = config.circuit_breaker.closed.burnin_period,
                            closed_failure_rate_threshold = config.circuit_breaker.closed.failure_rate_threshold,
                            half_open_window_size = config.circuit_breaker.half_open.window_size,
                            half_open_failure_rate_threshold = config.circuit_breaker.half_open.failure_rate_threshold,
                            half_open_delay = config.circuit_breaker.half_open.delay,
                            short_circuit_errors_window_size = config.circuit_breaker.short_circuit_errors.window_size,
                            short_circuit_errors_failure_rate_threshold = config.circuit_breaker.short_circuit_errors.failure_rate_threshold,
                            short_circuit_404s_window_size = config.circuit_breaker.short_circuit_404s.window_size,
                            short_circuit_404s_failure_rate_threshold = config.circuit_breaker.short_circuit_404s.failure_rate_threshold,
                            open_cooldown_period = config.circuit_breaker.open.cooldown_period
                                    )


# ------------------------------------------------------------------------------------------------ #
#                                         WEB                                                      #
# ------------------------------------------------------------------------------------------------ #
class WebContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    athrottle = providers.Singleton(AThrottle,
                                    min_rate=config.request.athrottle.min_rate,
                                    base_rate=config.request.athrottle.base_rate,
                                    max_rate=config.request.athrottle.max_rate,
                                    temperature=config.request.athrottle.temperature,
                                    window_size=config.request.athrottle.window_size,
                                    burn_in=config.request.athrottle.burn_in,
                                    )
    asession_appdata = providers.Singleton(ASessionAppData,
                                           throttle=athrottle,
                                           max_concurrency=config.request.asession.max_concurrency,
                                           retries=config.request.asession.retries,
                                           timeout=config.request.asession.timeout,
                                           )

    asession_review = providers.Singleton(ASessionReview,
                                           throttle=athrottle,
                                           max_concurrency=config.request.asession.max_concurrency,
                                           retries=config.request.asession.retries,
                                           timeout=config.request.asession.timeout,
                                           )
# ------------------------------------------------------------------------------------------------ #
#                                       FRAMEWORK                                                  #
# ------------------------------------------------------------------------------------------------ #
class AppStoreStreamContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    logs = providers.Container(LoggingContainer, config=config)

    data = providers.Container(PersistenceContainer)

    state = providers.Container(StateContainer, config=config)

    job = providers.Container(JobContainer, config=config)

    web = providers.Container(WebContainer, config=config)