#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/container.py                                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 04:17:11 am                                                 #
# Modified   : Tuesday August 27th 2024 10:23:58 am                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Framework Dependency Container"""
import logging
import logging.config  # pragma: no cover

from dependency_injector import containers, providers

from appvocai.infra.base.config import Config
from appvocai.infra.web.adapter import (
    Adapter,
    AdapterBaselineStage,
    AdapterConcurrencyExploreStage,
    AdapterExploitStage,
    AdapterRateExploreStage,
)

# from appstorestream.infra.web.asession import ASession
from appvocai.infra.web.profile import SessionHistory


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
#                                       ASESSION                                                   #
# ------------------------------------------------------------------------------------------------ #
# class AdapterContainer(containers.DeclarativeContainer):

#     config = providers.Configuration()

#     # Stages
#     baseline = providers.Singleton(AdapterBaselineStage, config=config.adapter.baseline)
#     rate = providers.Singleton(
#         AdapterRateExploreStage, config=config.adapter.explore_rate
#     )
#     concurrency = providers.Singleton(
#         AdapterConcurrencyExploreStage, config=config.adapter.explore_concurrency
#     )
#     exploit = providers.Singleton(AdapterExploitStage, config=config.adapter.exploit)

#     # Adapter
#     adapter = providers.Singleton(Adapter, initial_stage=baseline)

#     # Session History
#     history = providers.Singleton(SessionHistory, max_history=config.asession.history)

#     # Asynchronous Session
#     asession = providers.Singleton(
#         ASession,
#         adapter=adapter,
#         history=history,
#         retries=config.asession.retries,
#         timeout=config.asession.timeout,
#         concurrency=config.asession.concurrency.base,
#     )


# ------------------------------------------------------------------------------------------------ #
#                                       FRAMEWORK                                                  #
# ------------------------------------------------------------------------------------------------ #
class AppStoreStreamContainer(containers.DeclarativeContainer):

    config_filepath = Config().filepath

    config = providers.Configuration(yaml_files=[config_filepath])

    logs = providers.Container(LoggingContainer, config=config)

    # session = providers.Container(AdapterContainer, config=config)
