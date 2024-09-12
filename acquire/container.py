#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /acquire/container.py                                                               #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 04:17:11 am                                                 #
# Modified   : Wednesday September 11th 2024 09:21:42 pm                                           #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Framework Dependency Container"""
import logging
import logging.config  # pragma: no cover

import aiohttp
from dependency_injector import containers, providers

from acquire.infra.base.config import Config
from acquire.infra.database.mysql import MySQLDatabase
from acquire.infra.monitor.errors import log_error
from acquire.infra.monitor.extract import ExtractMonitorDecorator
from acquire.infra.repo.monitor.errors import ErrorLogRepo
from acquire.infra.repo.monitor.extract import ExtractMetricsRepo
from acquire.infra.web.adapter import (
    Adapter,
    AdapterBaselineStage,
    AdapterConcurrencyExploreStage,
    AdapterExploitStage,
    AdapterFactory,
    AdapterRateExploreStage,
)
from acquire.infra.web.asession import AsyncSession
from acquire.infra.web.profile import SessionHistory


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
#                                       MONITOR                                                    #
# ------------------------------------------------------------------------------------------------ #
class MonitorContainer(containers.DeclarativeContainer):

    db = providers.DependenciesContainer()

    metrics_extract_repo = providers.Singleton(ExtractMetricsRepo, database=db.mysql)

    metrics_extract = providers.Singleton(
        ExtractMonitorDecorator, repo=metrics_extract_repo
    )

    error_repo = providers.Singleton(ErrorLogRepo, database=db.mysql)

    error = providers.Callable(log_error, repo=error_repo)


# ------------------------------------------------------------------------------------------------ #
#                                      DATABASE                                                    #
# ------------------------------------------------------------------------------------------------ #
class DatabaseContainer(containers.DeclarativeContainer):

    mysql = providers.Singleton(MySQLDatabase)


# ------------------------------------------------------------------------------------------------ #
#                                 EXTRACTOR CONTAINER                                              #
# ------------------------------------------------------------------------------------------------ #
class AsyncSessionContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    # Dummy cookie jar which does not store cookies but ignores them.
    # An aiohttp.ClientSession dependency.
    cookie_jar = providers.Singleton(aiohttp.DummyCookieJar)

    # Connector for working with HTTP and HTTPS via TCP sockets.
    connector = providers.Singleton(
        aiohttp.TCPConnector,
        use_dns_cache=config.async_session.connector.use_dns_cache,
        ttl_dns_cache=config.async_session.connector.ttl_dns_cache,
        limit=config.async_session.connector.limit,
        limit_per_host=config.async_session.connector.limit_per_host,
        enable_cleanup_closed=config.async_session.connector.enable_cleanup_closed,
        keepalive_timeout=config.async_session.connector.keepalive_timeout,
        force_close=config.async_session.connector.force_close,
        happy_eyeballs_delay=config.async_session.connector.happy_eyeballs_delay,
    )

    # Controls the adapter metrics and statistics history
    history = providers.Singleton(SessionHistory, max_history=config.adapter.history)

    # The four rate and concurrency adapter stages are defined here.
    # 1. Baseline adapter stage: Gathers baseline statistics
    adapter_baseline_stage = providers.Singleton(
        AdapterBaselineStage, config=config.adapter.baseline
    )

    # 2. Rate Explore Stage: Optimizes request rate given baseline statistics
    adapter_explore_rate_stage = providers.Singleton(
        AdapterRateExploreStage, config=config.adapter.explore_rate
    )

    # 3. Explore Concurrency: Tunes concurrency to current performance
    adapter_explore_concurrency_stage = providers.Singleton(
        AdapterConcurrencyExploreStage, config=config.adapter.explore_concurrency
    )

    # 4. Exploit Stage: Adjusts request rate based on conditions
    adapter_exploit_stage = providers.Singleton(
        AdapterExploitStage, config=config.adapter.exploit
    )

    # 5. Create the Adapter Factory
    adapter_factory = providers.Singleton(
        AdapterFactory,
        adapter=Adapter,
        history=history,
        baseline=adapter_baseline_stage,
        explore_rate=adapter_explore_rate_stage,
        explore_concurrency=adapter_explore_concurrency_stage,
        exploit=adapter_exploit_stage,
    )

    # 6. Instantiate AsyncSession
    async_session = providers.Singleton(
        AsyncSession,
        connector=connector,
        cookie_jar=cookie_jar,
        adapter_factory=adapter_factory,
    )


# ------------------------------------------------------------------------------------------------ #
#                                       FRAMEWORK                                                  #
# ------------------------------------------------------------------------------------------------ #
class AppVoCAIContainer(containers.DeclarativeContainer):

    config_filepath = Config().filepath

    config = providers.Configuration(yaml_files=[config_filepath])

    logs = providers.Container(LoggingContainer, config=config)

    db = providers.Container(DatabaseContainer)

    monitor = providers.Container(MonitorContainer, db)
