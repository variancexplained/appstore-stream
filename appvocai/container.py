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
# Modified   : Tuesday September 3rd 2024 05:07:03 pm                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Framework Dependency Container"""
import logging
import logging.config  # pragma: no cover

from dependency_injector import containers, providers

from appvocai.infra.observer.extract import ObserverExtractorMetrics
from appvocai.infra.observer.load import ObserverLoadMetrics
from appvocai.infra.observer.transform import ObserverTransformMetrics
from appvocai.core.enum import ContentType
from appvocai.infra.base.config import Config
from appvocai.infra.database.mysql import MySQLDatabase
from appvocai.infra.web.adapter import (Adapter, AdapterBaselineStage,
                                        AdapterConcurrencyExploreStage,
                                        AdapterExploitStage,
                                        AdapterRateExploreStage)
from appvocai.infra.web.extractor import ASession
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

    mysql = providers.Singleton(MySQLDatabase)
# ------------------------------------------------------------------------------------------------ #
#                                       SESSION                                                    #
# ------------------------------------------------------------------------------------------------ #
class SessionContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    history = providers.Singleton(SessionHistory)

    session = providers.Singleton(ASession)

# ------------------------------------------------------------------------------------------------ #
#                                   METRICS OBSERVERS                                              #
# ------------------------------------------------------------------------------------------------ #
class ObserverContainer(containers.DeclarativeContainer):

    extractor_observer = providers.Singleton(ObserverExtractorMetrics, content_type=ContentType.APPDATA)
    transform_observer = providers.Singleton(ObserverTransformMetrics, content_type=ContentType.APPDATA)
    load_observer = providers.Singleton(ObserverLoadMetrics, content_type=ContentType.APPDATA)



# ------------------------------------------------------------------------------------------------ #
#                                       FRAMEWORK                                                  #
# ------------------------------------------------------------------------------------------------ #
class AppVoCAIContainer(containers.DeclarativeContainer):

    config_filepath = Config().filepath

    config = providers.Configuration(yaml_files=[config_filepath])

    logs = providers.Container(LoggingContainer, config=config)

    db = providers.Container(PersistenceContainer)

    web = providers.Container(SessionContainer, config=config)

    observe = providers.Container(ObserverContainer)
