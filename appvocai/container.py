#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/container.py                                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 04:17:11 am                                                 #
# Modified   : Friday September 6th 2024 05:48:26 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Framework Dependency Container"""
import logging
import logging.config  # pragma: no cover

from dependency_injector import containers, providers

from appvocai.infra.base.config import Config
from appvocai.infra.database.mysql import MySQLDatabase

# from appvocai.infra.web.asession import AsyncSession


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

    mysql = providers.Singleton(MySQLDatabase)


# ------------------------------------------------------------------------------------------------ #
#                                 EXTRACTOR CONTAINER                                              #
# ------------------------------------------------------------------------------------------------ #
# class AsyncSessionContainer(containers.DeclarativeContainer):

#     config = providers.Configuration()

#     # Dummy cookie jar which does not store cookies but ignores them.
#     # An aiohttp.ClientSession dependency.
#     cookie_jar = providers.Singleton(aiohttp.DummyCookieJar)

#     # Connector for working with HTTP and HTTPS via TCP sockets.
#     connector = providers.Singleton(
#         aiohttp.TCPConnector,
#         use_dns_cache=config.async_session.connector.use_dns_cache,
#         ttl_dns_cache=config.async_session.connector.ttl_dns_cache,
#         limit=config.async_session.connector.limit,
#         limit_per_host=config.async_session.connector.limit_per_host,
#         enable_cleanup_closed=config.async_session.connector.enable_cleanup_closed,
#         keepalive_timeout=config.async_session.connector.keepalive_timeout,
#         force_close=config.async_session.connector.force_close,
#         happy_eyeballs_delay=config.async_session.connector.happy_eyeballs_delay,
#     )

#     # Controls the adapter metrics and statistics history
#     history = providers.Singleton(SessionHistory, max_history=config.adapter.history)

#     # The four rate and concurrency adapter stages are defined here.
#     # 1. Baseline adapter stage: Gathers baseline statistics
#     adapter_baseline_stage = providers.Singleton(
#         AdapterBaselineStage, config=config.adapter.baseline
#     )

#     # 2. Rate Explore Stage: Optimizes request rate given baseline statistics
#     adapter_explore_rate_stage = providers.Singleton(
#         AdapterRateExploreStage, config=config.adapter.explore_rate
#     )

#     # 3. Explore Concurrency: Tunes concurrency to current performance
#     adapter_explore_concurrency_stage = providers.Singleton(
#         AdapterConcurrencyExploreStage, config=config.adapter.explore_concurrency
#     )

#     # 4. Exploit Stage: Adjusts request rate based on conditions
#     adaptor_exploit_stage = providers.Singleton(
#         AdapterExploitStage, config=config.adapter.exploit
#     )


# ------------------------------------------------------------------------------------------------ #
#                                       FRAMEWORK                                                  #
# ------------------------------------------------------------------------------------------------ #
class AppVoCAIContainer(containers.DeclarativeContainer):

    config_filepath = Config().filepath

    config = providers.Configuration(yaml_files=[config_filepath])

    logs = providers.Container(LoggingContainer, config=config)

    db = providers.Container(PersistenceContainer)
