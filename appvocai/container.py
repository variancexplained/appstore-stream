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
# Modified   : Thursday August 29th 2024 06:23:22 pm                                               #
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
from appvocai.infra.web.adapter import (Adapter, AdapterBaselineStage,
                                        AdapterConcurrencyExploreStage,
                                        AdapterExploitStage,
                                        AdapterRateExploreStage)
# from appvocai.infra.web.asession import ASession
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
#                                      PERSISTENCE                                                 #
# ------------------------------------------------------------------------------------------------ #
class PersistenceContainer(containers.DeclarativeContainer):

    database = providers.Singleton(MySQLDatabase)
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
class appvocaiContainer(containers.DeclarativeContainer):

    config_filepath = Config().filepath

    config = providers.Configuration(yaml_files=[config_filepath])

    logs = providers.Container(LoggingContainer, config=config)

    # session = providers.Container(AdapterContainer, config=config)
